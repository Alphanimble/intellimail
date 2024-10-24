class Features:
    def __init__(self):
        self.sender_full_name = ""
        self.reciever_full_name = ""
        self.sender_first_name = ""
        self.sender_last_name = ""
        self.reciever_first_name = ""
        self.reciever_last_name = ""
        self.sender_email = ""
        self.reciever_email =""
        self.sender_org = ""
        self.reciever_org = ""
        self.subject=""
        self.body = ""
        self.date = ""
        self.message_id=""
        self.word_count = 0
        self.summarised_body = ""
        self.named_entities = {}
        self.phone_numbers = []

    def populate_name(self):
        # Check if sender_full_name is set
        if self.sender_full_name:
            self.sender_first_name = self.sender_full_name.split()[0] if '@' not in self.sender_full_name.split()[0] else self.sender_org
            self.sender_last_name = self.sender_full_name.split()[-1] if '@' not in self.sender_full_name.split()[-1] else self.sender_org
            self.sender_last_name = "" if str(self.sender_first_name).strip() == str(self.sender_last_name).strip() else self.sender_last_name
        else:
            self.sender_first_name = ""
            self.sender_last_name = ""

        # Check if reciever_full_name is set
        if self.reciever_full_name:
            self.reciever_first_name = self.reciever_full_name.split()[0] if '@' not in self.reciever_full_name.split()[0] else self.reciever_org
            self.reciever_last_name = self.reciever_full_name.split()[-1] if '@' not in self.reciever_full_name.split()[-1] else self.reciever_org
            self.reciever_last_name = "" if str(self.reciever_first_name).strip() == str(self.reciever_last_name).strip() else self.reciever_last_name
        else:
            self.reciever_first_name = ""
            self.reciever_last_name = ""

    def fix_body(self):
        return self.body.replace("'", "\\'")

    def __str__(self):
        return f"{self.date}\n,{self.body}\n,{self.reciever_org}\n,{self.sender_org}\n,{self.reciever_email}\n,{self.sender_email}\n"
