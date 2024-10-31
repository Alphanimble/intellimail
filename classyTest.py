import spacy

data = {
    "seeking investment": [
        "We are seeking immediate investment for our startup.",
        "Looking for funding opportunities.",
        "Capital raise for expansion.",
    ],
    "exploring partnership": [
        "We are exploring future partnership opportunities.",
        "Interested in collaborating with your company.",
        "Pitch deck for potential partnership.",
    ],
    "requesting information": [
        "I am interested in learning more about your services.",
        "Could you please provide more information?",
        "I have a query regarding your products.",
    ],
    "following up": [
        "Following up on our previous conversation.",
        "I would like additional details as requested.",
        "More information is needed.",
    ],
    "making introduction": [
        "I wanted to connect with you.",
        "I am introducing John, our new team member.",
        "I'd like to make an introduction.",
    ],
    "discussion": [
        "Let's discuss the project details.",
        "I'd like to have a discussion about the proposal.",
        "Discussing potential solutions.",
    ],
    "meeting schedule": [
        "I would like to schedule a meeting.",
        "Let's chat about the project.",
        "Could we have a call to discuss further?",
    ],
    "task assignment": [
        "I have assigned a new task to the team.",
        "Could you please take care of this task?",
        "Task delegation for the upcoming project.",
    ],
    "task scheduled": [
        "The task has been scheduled for next week.",
        "The meeting is scheduled for tomorrow.",
        "I have scheduled a follow-up call for next month.",
    ],
    "sharing document": [
        "I am sharing the project documentation.",
        "Please find the attached document.",
        "I have sent you the required documents.",
    ],
    "update": [
        "I would like to update you on the project progress.",
        "There has been an update in the project timeline.",
        "I have an update regarding the meeting.",
    ],
    "documentation": [
        "I need to update the project documentation.",
        "Could you please provide the necessary documentation?",
        "I have reviewed the documentation.",
    ],
}

nlp = spacy.blank("en")
nlp.add_pipe(
    "classy_classification",
    config={
        "data": data,
        "model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "device": "gpu",
    },
)


def categorize_mail(obj):
    doc = nlp(obj.body)
    cats = doc._.cats
    predicted_category = max(cats, key=cats.get)
    print(f"{predicted_category}")
    return predicted_category


# print(nlp("We are seeking immediate investment for our startup.")._.cats)
#
# text = "hey can you share the documents needed for this library"
# cats = nlp(text)._.cats
#
# # Get the category with the highest probability
# predicted_category = max(cats, key=cats.get)
#
# print(f"The predicted category is: {predicted_category}")
