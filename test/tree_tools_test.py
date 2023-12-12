import pytest
from src.valid_index import ValidIndex, get_banking_act_index
from src.tree_tools import TreeNode, Tree, split_tree, build_tree_for_regulation
from src.file_tools import process_lines, add_full_reference


class TestTree:
    index_checker = get_banking_act_index()

    def test_add_to_tree(self):
        tree = Tree("BA", self.index_checker)
        invalid_reference = '23(1)(c)(xviii)(A)(A)(cc)'
        with pytest.raises(ValueError):
            tree.add_to_tree(invalid_reference, heading_text='')

        #Check all nodes get added
        valid_index = '23(1)(a)(iv)(I)(i)(cc)(iii)(d)'
        tree.add_to_tree(valid_index, heading_text='Some really deep heading here')
        number_of_nodes = sum(1 for _ in tree.root.descendants) # excludes the root node
        assert number_of_nodes == 9

        #check that if a duplicate is added, it does not increase the node count
        sub_index = '23(1)(a)(iv)(I)'
        tree.add_to_tree(valid_index, heading_text='Some less deep heading here')
        number_of_nodes = sum(1 for _ in tree.root.descendants) # excludes the root node
        assert number_of_nodes == 9



    def test_get_node(self):
        tree = Tree("BA", self.index_checker)
        invalid_reference = '23(1)(a)(iv)(I)'
        with pytest.raises(ValueError):
            tree.get_node(invalid_reference)
        invalid_reference = ''
        with pytest.raises(ValueError):
            tree.get_node(invalid_reference)
        
        assert tree.get_node("BA") == tree.root
        assert tree.get_node("BA").full_node_name == ""
        assert tree.get_node("BA").heading_text == ""

        ba_description = "South African Bank's Act"
        tree.add_to_tree("BA", heading_text=ba_description)
        assert tree.get_node("BA").heading_text == ba_description

        valid_index = '23(1)(a)(iv)(I)(i)(cc)(iii)(d)'
        tree.add_to_tree(valid_index, heading_text='Some really deep heading here')
        assert tree.get_node(valid_index).heading_text == 'Some really deep heading here'
        sub_index = '23(1)(a)(iv)(I)'
        assert tree.get_node(sub_index).heading_text == ''
        tree.add_to_tree(sub_index, heading_text='Some less deep heading here')
        assert tree.get_node(sub_index).heading_text == 'Some less deep heading here'


def test_split_tree():

    lines = []
    lines.append('(3) Duties and responsibilities of Authorised Dealers (#Heading) (reference_pdf_document_1.pdf; pg 1)')
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

    ba_index = get_banking_act_index()
    df = process_lines(lines, ba_index)
    add_full_reference(df, ba_index, '23')

    tree = build_tree_for_regulation("split_test", df, ba_index)

    #node_list=[]
    token_limit_per_chunk = 125
    chunked_df = split_tree(tree.root, df, token_limit_per_chunk, ba_index)
    assert len(chunked_df) == 7
    assert chunked_df.iloc[0]['section'] == '23(3)(a)(i)'
    assert chunked_df.iloc[1]['section'] == '23(3)(a)(ii)'
    assert chunked_df.iloc[2]['section'] == '23(3)(b)(i)'
    assert chunked_df.iloc[6]['section'] == '23(3)(e)(viii)(A)(iii)'

