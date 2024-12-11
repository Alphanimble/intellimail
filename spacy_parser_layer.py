import spacy
from spacy import displacy

nlp = spacy.load("en_core_web_sm")
#
# doc = nlp("\nGeorge,\n\n Below is a list of questions that Keith and I had regarding the Westgate \nproject:\n\n Ownership Structure\n\n What will be the ownership structure? Limited partnership? General partner?\n\n What are all the legal entities that will be involved and in what \ncapacity(regarding ownership and \n liabilities)?\n\n Who owns the land? improvements?\n\n Who holds the various loans?\n\n Is the land collateral?\n\n Investment\n \n What happens to initial investment?\n\n Is it used to purchase land for cash?Secure future loans?\n \n Why is the land cost spread out on the cash flow statement?\n\n When is the 700,000 actually needed? Now or for the land closing? Investment \nschedule?\n\n Investment Return\n\n Is Equity Repayment the return of the original investment?\n\n Is the plan to wait until the last unit is sold and closed before profits \nare distributed?\n\n Debt\n\n Which entity is the borrower for each loan and what recourse or collateral \nis associated with each \n loan?\n\n Improvement\n\n Construction\n\n Are these the only two loans?  Looks like it from the cash flow statement.\n\n Terms of each loan?\n\n Uses of Funds\n\n How will disbursements be made?  By whom?\n\n What type of bank account?  Controls on max disbursement? Internet viewing \nfor investors?\n\n Reports to track expenses vs plan?\n\n Bookkeeping procedures to record actual expenses?\n\n What is the relationship of Creekside Builders to the project?  Do you get \npaid a markup on subcontractors as a \n general contractor and paid gain out of profits?\n\n Do you or Larry receive any money in the form of salary or personal expenses \nbefore the ultimate payout of profits?\n\n Design and Construction\n \n When will design be complete?\n\n What input will investors have in selecting design and materials for units?\n\n What level of investor involvement will be possible during construction \nplanning and permitting?\n\n Does Creekside have specific procedures for dealing with subcontractors, \nvendors, and other professionals? \n Such as always getting 3 bids, payment schedules, or reference checking?\n\n Are there any specific companies or individuals that you already plan to \nuse? Names?\n\nThese questions are probably very basic to you, but as a first time investor \nin a project like this it is new to me.  Also, I want to learn as\nmuch as possible from the process.\n\nPhillip\n\n\n\n\n\n\n\n\n\n\n \n \n\n \n\n  \n\n")
# displacy.render(doc,style="ent")


def process_features(obj_list):
    nlp = spacy.load("en_core_web_sm")
    i = 0
    for objs in obj_list:
        doc = nlp(objs.body)
        objs.word_count = sum(1 for token in doc if token.text.isalnum())
        named_entity_lists = {}
        for ent in doc.ents:
            if ent.label_ not in named_entity_lists:
                ent_list = []
                ent_list.append(str(ent))
                named_entity_lists[ent.label_] = ent_list
            else:
                named_entity_lists[ent.label_].append(str(ent))
        objs.named_entities = named_entity_lists
        print(i)
        i += 1


def get_word_count(text):
    doc = nlp(text)
    word_count = sum(1 for token in doc if token.text.isalnum())
    return word_count


def get_entities(text):
    doc = nlp(text)
    named_entity_lists = {}
    for ent in doc.ents:
        if ent.label_ not in named_entity_lists:
            ent_list = []
            ent_list.append(str(ent))
            named_entity_lists[ent.label_] = ent_list
        else:
            named_entity_lists[ent.label_].append(str(ent))
    return named_entity_lists
