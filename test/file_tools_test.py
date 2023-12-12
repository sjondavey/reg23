import pytest
import pandas as pd
import os
import fnmatch

from src.valid_index import ValidIndex, get_banking_act_index
from src.file_tools import  add_full_reference, \
                            read_processed_regs_into_dataframe, \
                            extract_non_text, \
                            process_lines, \
                            get_regulation_detail


def test_extract_non_text():
    # Data as expected
    block_identifier = '#Table'
    lines = []
    lines.append('A.2 Authorised entities (#Heading)')
    lines.append('    (A) Authorised Dealers (#Heading)')
    lines.append('    The offices in South Africa of the under-mentioned banks in Table 1 are authorised to act, for the purposes of the Regulations, as Authorised Dealers: ')
    lines.append('        #Table 1')
    lines.append('            Name of entity - Authorised Dealer')
    lines.append('            ABSA Bank Limited')
    lines.append('        #Table 1 - end')
    remaining_lines, dictionary = extract_non_text(lines, block_identifier)
    assert len(dictionary) == 1
    assert len(dictionary['#Table 1']) == 2
    assert len(remaining_lines) == 3

    # No -end marker but many lines of text
    lines = []
    lines.append('A.2 Authorised entities (#Heading)')
    lines.append('    (A) Authorised Dealers (#Heading)')
    lines.append('    The offices in South Africa of the under-mentioned banks in Table 1 are authorised to act, for the purposes of the Regulations, as Authorised Dealers: ')
    lines.append('        #Table 1')
    for i in range(110):
        lines.append(f'            Entity {i}')
    lines.append('    More text without the ending the table')
    with pytest.raises(ValueError):
        remaining_lines, dictionary = extract_non_text(lines, block_identifier)

    # No -end marker and we reach the end of the data
    lines = []
    lines.append('A.2 Authorised entities (#Heading)')
    lines.append('    (A) Authorised Dealers (#Heading)')
    lines.append('    The offices in South Africa of the under-mentioned banks in Table 1 are authorised to act, for the purposes of the Regulations, as Authorised Dealers: ')
    lines.append('        #Table 1')
    lines.append('            Name of entity - Authorised Dealer')
    lines.append('            ABSA Bank Limited')
    with pytest.raises(ValueError):
        remaining_lines, dictionary = extract_non_text(lines, block_identifier)
    
def test_process_lines():
    lines = []
    lines.append('(1) Duties and responsibilities of Authorised Dealers (#Heading) (reference_pdf_document_1.pdf; pg 1)')
    lines.append('some preamble with no reference, but correct spacing here')
    lines.append('    (a) Introduction (#Heading) (reference_pdf_document_1.pdf; pg 2)')
    lines.append('        (i) Authorised Dealers should note that when approving requests in terms of the Authorised Dealer Manual, they are in terms of the Regulations, not allowed to grant permission to clients and must refrain from using wording that approval/permission is granted in correspondence with their clients. Instead reference should be made to the specific section of the Authorised Dealer Manual in terms of which the client is permitted to transact. (reference_pdf_document_2.pdf; pg 1)')
    lines.append('        (ii) In carrying out the important duties entrusted to them, Authorised Dealers should appreciate that uniformity of policy is essential, and that to ensure this it is necessary for the Regulations, Authorised Dealer Manual and circulars to be applied strictly and impartially by all concerned. ')
    lines.append('    (b) Procedures to be followed by Authorised Dealers in administering the Exchange Control Regulations (#Heading)')
    lines.append('        (i) In cases where an Authorised Dealer is uncertain and/or cannot approve the purchase or sale of foreign currency or any other transaction in terms of the authorities set out in the Authorised Dealer Manual, an application should be submitted to the Financial Surveillance Department via the head office of the Authorised Dealer concerned. ')
    lines.append('        (ii) Should an Authorised Dealer have any doubt as to whether or not it may approve an application, such application must likewise be submitted to the Financial Surveillance Department. Authorised Dealers must as a general rule, refrain from their own interpretation of the Authorised Dealer Manual. ')
    lines.append('')
    lines.append('  ')
    lines.append('    (e) Transactions with Common Monetary Area residents (#Heading)')
    lines.append('        (viii) As an exception to (vi) above, Authorised Dealers may:') 
    lines.append('            (A) sell foreign currency to: ')
    lines.append('                (i) foreign diplomats, accredited foreign diplomatic staff as well as students with a valid student card from other CMA countries while in South Africa; ')
    lines.append('                (ii) CMA residents in South Africa, to cover unforeseen incidental costs whilst in transit, subject to viewing a passenger ticket confirming a destination outside the CMA;  ')

    index_checker = get_banking_act_index()
    df = process_lines(lines, index_checker)
    assert len(df) == len(lines) - 2 #strip out blank lines
    assert len(df[df['Document'] != ""]) == 3
    assert df.iloc[0]['Document'] == "reference_pdf_document_1.pdf"
    assert df.iloc[0]['Page'] == "1"
    assert df.iloc[3]['Document'] == "reference_pdf_document_2.pdf"
    assert df.iloc[3]['Page'] == "1"
    assert len(df[df["Heading"]]) == 4
    assert len(df[df['Reference'] != ""]) == len(df) - 1


def test_add_full_reference():    
    index_checker = get_banking_act_index()
    # Sample DataFrame
    df = pd.DataFrame({
    'Indent':    [ 0,    0,    1,     2,      3,     2,     2],
    'Reference': ['(1)', '', '(b)', '(vii)', '(C)', '(xvi)', ''],
    'Text' :     ['1',   '2', '3',  '4',      '5',   '6',    '7']
    })
    add_full_reference(df, index_checker, '23')
    assert df.loc[0, 'full_reference'] == '23(1)'
    assert df.loc[1, 'full_reference'] == '23(1)'
    assert df.loc[2, 'full_reference'] == '23(1)(b)'
    assert df.loc[3, 'full_reference'] == '23(1)(b)(vii)'
    assert df.loc[4, 'full_reference'] == '23(1)(b)(vii)(C)'
    assert df.loc[5, 'full_reference'] == '23(1)(b)(xvi)'
    assert df.loc[6, 'full_reference'] == '23(1)(b)(xvi)'

    df_with_indent_reference_mismatch = pd.DataFrame({
    'Indent':    [ 0,    0,    1,     2,      3,     2,     2],
    'Reference': ['(1)', '', '(B)', '(vii)', '(C)', '(D)', ''],
    'Text':      ['1',   '2','3',   '4',   '5',   '6',   '7']
    })
    with pytest.raises(ValueError):
        add_full_reference(df_with_indent_reference_mismatch, index_checker)

def test_get_regulation_detail():
    lines = []
    lines.append('(1) Duties and responsibilities of Authorised Dealers (#Heading) (reference_pdf_document_1.pdf; pg 1)')
    lines.append('some preamble with no reference, but correct spacing here')
    lines.append('    (a) Introduction (#Heading) (reference_pdf_document_1.pdf; pg 2)')
    lines.append('        (i) Authorised Dealers should note that when approving requests in terms of the Authorised Dealer Manual, they are in terms of the Regulations, not allowed to grant permission to clients and must refrain from using wording that approval/permission is granted in correspondence with their clients. Instead reference should be made to the specific section of the Authorised Dealer Manual in terms of which the client is permitted to transact. (reference_pdf_document_2.pdf; pg 1)')
    lines.append('        (ii) In carrying out the important duties entrusted to them, Authorised Dealers should appreciate that uniformity of policy is essential, and that to ensure this it is necessary for the Regulations, Authorised Dealer Manual and circulars to be applied strictly and impartially by all concerned. ')
    lines.append('    (b) Procedures to be followed by Authorised Dealers in administering the Exchange Control Regulations (#Heading)')
    lines.append('        (i) In cases where an Authorised Dealer is uncertain and/or cannot approve the purchase or sale of foreign currency or any other transaction in terms of the authorities set out in the Authorised Dealer Manual, an application should be submitted to the Financial Surveillance Department via the head office of the Authorised Dealer concerned. ')
    lines.append('        (ii) Should an Authorised Dealer have any doubt as to whether or not it may approve an application, such application must likewise be submitted to the Financial Surveillance Department. Authorised Dealers must as a general rule, refrain from their own interpretation of the Authorised Dealer Manual. ')
    lines.append('    (e) Transactions with Common Monetary Area residents (#Heading)')
    lines.append('    Pre-amble to (e)')
    lines.append('        (viii) As an exception to (vi) above, Authorised Dealers may:') 
    lines.append('            (A) sell foreign currency to: ')
    lines.append('                (i) foreign diplomats, accredited foreign diplomatic staff as well as students with a valid student card from other CMA countries while in South Africa; ')
    lines.append('                (ii) CMA residents in South Africa, to cover unforeseen incidental costs whilst in transit, subject to viewing a passenger ticket confirming a destination outside the CMA;  ')
    lines.append('                (iii) CMA residents in South Africa, to cover unforeseen incidental costs whilst in transit, subject to viewing a passenger ticket confirming a destination outside the CMA;  ')
    lines.append('    Post-amble to (e)')
    lines.append('some post-amble with no reference, but correct spacing here')

    index_checker = get_banking_act_index()
    df = process_lines(lines, index_checker)
    add_full_reference(df, index_checker, '23')

    response = get_regulation_detail('23(1)(e)(viii)(A)(ii)', df, index_checker)
    expected_response = '(1) Duties and responsibilities of Authorised Dealers\n\
some preamble with no reference, but correct spacing here\n\
    (e) Transactions with Common Monetary Area residents\n\
    Pre-amble to (e)\n\
        (viii) As an exception to (vi) above, Authorised Dealers may:\n\
            (A) sell foreign currency to:\n\
                (ii) CMA residents in South Africa, to cover unforeseen incidental costs whilst in transit, subject to viewing a passenger ticket confirming a destination outside the CMA;\n\
    Post-amble to (e)\n\
some post-amble with no reference, but correct spacing here'
    assert response == expected_response

# Don't need to do this in the ChatBot app
def test_read_processed_regs_into_dataframe():
    index_checker = get_banking_act_index()
    non_text_labels = ['Table', 'Formula', 'Example', 'Definition']
    dir_path = './test/data/'
    file_list = []
    for root, dir, files in os.walk(dir_path):
        for file in files:
            str = 'reg23*.txt'
            if fnmatch.fnmatch(file, str):
                file_path = os.path.join(root, file)
                file_list.append(file_path)
    df_excon, non_text = read_processed_regs_into_dataframe(file_list=file_list, valid_index_checker=index_checker, non_text_labels=non_text_labels)
    assert len(df_excon) == 2341
    assert len(non_text['Table']) == 24
    assert len(non_text['Definition']) == 1

