# Update the relevant summary row
from openai import OpenAI
client = OpenAI()

system_content_summerise = "You are summarising parts of Regulation 23 of the Banks Act (Reg23) for a bank that needs to complete the Credit Risk Monthly Return (Form BA 200). When summerising, do not add filler words like 'the act says ...' or 'Reg23 says ...', just summarise the section. Your summary should use plain language and avoid legalese. Since it is for a bank, when the act uses the phrase 'bank', please replace it with the relevant first person pronoun like 'I' or 'me'. A good summary will minimise the use of lists. Rather it should make use of paragraphs.\n\
Note: Reg23 offers two approaches to modelling credit risk namely the standardised approach and the internal ratings-based (IRB) approach. The standardised approach is subdivided into the 'Simplified Standardised' and the 'Standardised' approach. The IRB approach is subdivided into the 'Foundation IRB' (FIRB) and the 'Advanced IRB' (AIRB). The act will often refer to Method 1 or Method 2 but please use the full name or acronym of the appropriate calculation methodology in your summary."



system_content_question = "You are assisting a bank to comply with regulation 23 of the Banks Act (Reg23) by preparing a set of Frequently Asked Questions (FAQs). You will be provided with the Answer written in the first person from the point of view of the bank, your role to create one or two Questions for the Answer. The questions should focus on the high level concepts addressed in the Answer rather than the detail. Do not use the phrases like 'According to Reg 23 ...' or 'Under the act ...'. Just ask questions for which this is the answer.  List your questions as a pipe delimited string."


def get_summary_and_questions_for(text, model):

    user_context = text
    response = client.chat.completions.create(
                        model=model,
                        temperature = 1.0,
                        max_tokens = 500,
                        messages=[
                            {"role": "system", "content": system_content_summerise},
                            {"role": "user", "content": user_context},
                        ]
                    )
    if response.choices[0].finish_reason == "stop":
        summary = response.choices[0].message.content
    else:
        summary = ""
        print("Summary did not complete")
        print(response)


    user_context_question = summary
    if summary != "":
        response = client.chat.completions.create(
                            model=model,
                            temperature = 1.0,
                            max_tokens = 500,
                            messages=[
                                {"role": "system", "content": system_content_question},
                                {"role": "user", "content": user_context_question},
                            ]
                        )
        if response.choices[0].finish_reason == "stop":
            questions = response.choices[0].message.content
        else:
            print("Question did not complete")
            question = ""
            print(response)
    else:
        question = ""

    return summary, questions

