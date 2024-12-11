import os
import json
from typing import List, Dict, Optional
import logging
import time
from dotenv import load_dotenv
from mistralai import Mistral
import postgres_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MistralConversationalAgent:
    def __init__(self):
        """
        Initialize the conversational agent with Mistral API and configurations.
        """
        # Load environment variables
        load_dotenv()

        # Set up Mistral client
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment variables")
        
        self.mistral_client = Mistral(api_key=api_key)
        
        # Agent IDs (consider moving to environment variables)
        self.GENERATOR_AGENT_ID = "ag:66d97af1:20241209:untitled-agent:ec372937"
        self.RETRIEVAL_AGENT_ID = "ag:66d97af1:20241022:untitled-agent:3067016b"
        
        # Initialize conversation history
        self.conversation_history: List[Dict[str, str]] = []

    def process_generator_prompt(self) -> str:
        """
        Process prompt using the generator agent.
        
        Returns:
            str: Generated response content
        """
        try:
            chat_response = self.mistral_client.agents.complete(
                agent_id=self.GENERATOR_AGENT_ID,
                messages=self.conversation_history,
            )
            return chat_response.choices[0].message.content
        except Exception as e:
            logger.error(f"Generator prompt processing error: {e}")
            raise

    def process_retrieval_prompt(self, text: str) -> str:
        """
        Process retrieval prompt for generating SQL query.
        
        Args:
            text (str): Input text for retrieval
        
        Returns:
            str: Generated SQL query
        """
        try:
            chat_response = self.mistral_client.agents.complete(
                agent_id=self.RETRIEVAL_AGENT_ID,
                messages=[{"role": "user", "content": text}],
            )
            return chat_response.choices[0].message.content
        except Exception as e:
            logger.error(f"Retrieval prompt processing error: {e}")
            raise

    def execute_database_query(self, query: str) -> Optional[List[Dict]]:
        """
        Execute SQL query and return results.
        
        Args:
            query (str): SQL query to execute
        
        Returns:
            Optional list of query results or None
        """
        try:
            with postgres_connection.connect_to_postgres() as conn:
                return postgres_connection.execute_query(conn, query)
        except Exception as e:
            logger.error(f"Database query execution error: {e}")
            return None

    def run_conversation(self):
        """
        Main conversation loop handling user interactions.
        """
        print("Welcome! Start your conversation with the generator agent.")
        
        while True:
            try:
                # Get user input
                user_input = input("You: ")
                
                # Check for exit condition
                if user_input.lower() in {"exit", "quit"}:
                    print("Ending conversation. Goodbye!")
                    break
                
                # Process user input
                self.conversation_history.append({"role": "user", "content": user_input})
                
                # Generate initial response
                generator_response = self.process_generator_prompt()
                
                # Parse generator response
                response_json = json.loads(generator_response)
                bot_text = response_json.get("bot", "")
                
                if not bot_text:
                    logger.warning("No 'bot' parameter found in the response.")
                    continue
                
                # Add bot response to conversation history
                self.conversation_history.append({"role": "assistant", "content": bot_text})
                
                # Retrieve and execute database query
                query_result = self._retrieve_and_execute_query(bot_text)
                
                if query_result:
                    # Process query result with generator agent
                    self._process_query_result(query_result)
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON Decode Error: {e}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")

    def _retrieve_and_execute_query(self, bot_text: str) -> Optional[List[Dict]]:
        """
        Retrieve SQL query and execute it with data volume check.
        
        Args:
            bot_text (str): Text to generate SQL query
        
        Returns:
            Optional list of query results
        """
        while True:
            try:
                sql_query = self.process_retrieval_prompt(bot_text)
                logger.info(f"Generated SQL Query: {sql_query}")
                
                query_result = self.execute_database_query(sql_query)
                
                # Check query result size
                if query_result and len(str(query_result)) > 20000:
                    bot_text += " please retrieve smaller amount of data by by limiting the number of rows returned or getting only necessary columns "
                    logger.warning("Query result too large. Refining query.")
                    time.sleep(1)
                    continue
                
                return query_result
            
            except Exception as e:
                logger.error(f"Query retrieval/execution error: {e}")
                return None

    def _process_query_result(self, query_result: List[Dict]):
        """
        Process query result with generator agent.
        
        Args:
            query_result (List[Dict]): Database query results
        """
        generator_feedback = {"bot-response": query_result}
        self.conversation_history.append({
            "role": "user",
            "content": json.dumps(generator_feedback)
        })
        
        # Get generator's follow-up response
        generator_followup_response = self.process_generator_prompt()
        followup_response_json = json.loads(generator_followup_response)
        logger.info(f"Generator Follow-Up: {followup_response_json.get('user', '')}")

def main():
    """
    Entry point for the Mistral Conversational Agent.
    """
    agent = MistralConversationalAgent()
    agent.run_conversation()

if __name__ == "__main__":
    main()
