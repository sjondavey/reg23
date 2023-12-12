import pytest
from src.valid_index import ValidIndex, get_banking_act_index

class TestValidIndex:
    index_banking_act = get_banking_act_index()

    def test_is_valid_reference(self):
        blank_reference = ""
        assert not self.index_banking_act.is_valid_reference(blank_reference)

        long_reference = '23(1)(a)(iv)(I)(i)(cc)(iii)(d)'
        assert self.index_banking_act.is_valid_reference(long_reference)
        short_reference = '23(15)(d)'        
        assert self.index_banking_act.is_valid_reference(short_reference)


        invalid_reference = '23(1)(c)(xviii)(A)(A)(cc)'
        assert not self.index_banking_act.is_valid_reference(invalid_reference)
        invalid_reference = '23(10)(d)(xviii)(C)(iv)(9)'
        assert not self.index_banking_act.is_valid_reference(invalid_reference)
        invalid_reference = '(1)(a)(iv)(I)(i)(cc)(iii)(d)'
        assert not self.index_banking_act.is_valid_reference(invalid_reference)
        invalid_reference = '23(a)(iv)(I)(i)(cc)(iii)(d)'
        assert not self.index_banking_act.is_valid_reference(invalid_reference)

    def test_extract_valid_reference(self):
        assert self.index_banking_act.extract_valid_reference('23 subregulation (1)(a)(iv)(I)(i)(cc)(iii)(d)') == '23(1)(a)(iv)(I)(i)(cc)(iii)(d)'
        assert self.index_banking_act.extract_valid_reference('   23 subregulation (1)(a)(iv)    ') == '23(1)(a)(iv)'
        assert self.index_banking_act.extract_valid_reference('23 subregulation (1)(a)(iv)(I)(J)')  == '23(1)(a)(iv)(I)'
        assert self.index_banking_act.extract_valid_reference('23(10)') == '23(10)'
        assert self.index_banking_act.extract_valid_reference('23 subregulation (1)(a)(iv) hello (I) ') == '23(1)(a)(iv)(I)' # text at the end

    def test_split_reference(self):
        long_reference = '23(1)(a)(iv)(I)(i)(cc)(iii)(d)'
        components = self.index_banking_act.split_reference(long_reference)
        assert len(components) == 9
        assert components[0] == '23'
        assert components[1] == '(1)'
        assert components[2] == '(a)'
        assert components[3] == '(iv)'
        assert components[4] == '(I)'
        assert components[5] == '(i)'
        assert components[6] == '(cc)'
        assert components[7] == '(iii)'
        assert components[8] == '(d)'

        short_reference = '23(1)'        
        components = self.index_banking_act.split_reference(short_reference)
        assert len(components) == 2
        assert components[0] == '23'
        assert components[1] == '(1)'


        invalid_reference = '23(1)(c)(xviii)(A)(A)(cc)'
        with pytest.raises(ValueError):
            components = self.index_banking_act.split_reference(invalid_reference)

        invalid_reference = '(1)(a)(iv)(I)(i)(cc)(iii)(d)'
        with pytest.raises(ValueError):
            components = self.index_banking_act.split_reference(invalid_reference)

        # reference_on_exclusion_list = 'Legal context'
        # components = self.index_banking_act.split_reference(reference_on_exclusion_list)
        # assert components[0] == reference_on_exclusion_list

    def test_get_parent_reference(self):
        reference = '23(1)(c)(xviii)(A)'
        assert self.index_banking_act.get_parent_reference(reference) == '23(1)(c)(xviii)'
        with pytest.raises(ValueError):
            components = self.index_banking_act.get_parent_reference("")


    def test_parse_line_of_text(self):
        string_with_incorrect_indent = "               (ii) the bank duly specifies the treatment of individual entities in a connected group, including the circumstances under which the same rating may or may not be assigned to all or some related entities;"
        with pytest.raises(ValueError):
            indent, index, remaining_text = self.index_banking_act.parse_line_of_text(string_with_incorrect_indent)

        string_with_mismatched_indent_and_index = "        (A) shall be applied consistently over time for internal risk management purposes and in terms of the IRB approach;"
        with pytest.raises(ValueError):
            indent, index, remaining_text = self.index_banking_act.parse_line_of_text(string_with_mismatched_indent_and_index)

        string_with_correct_indent = "(11) Method 1: Calculation of credit risk exposure in terms of the foundation IRB approach (#Heading) (02-Regulations-part-2.pdf; pg 14)"
        indent, index, remaining_text = self.index_banking_act.parse_line_of_text(string_with_correct_indent)
        assert indent == 0
        assert index == '(11)'
        assert remaining_text == 'Method 1: Calculation of credit risk exposure in terms of the foundation IRB approach (#Heading) (02-Regulations-part-2.pdf; pg 14)'
        

        string_with_correct_indent = "                (iv) corporate governance process;"
        indent, index, remaining_text = self.index_banking_act.parse_line_of_text(string_with_correct_indent)
        assert indent == 4
        assert index == '(iv)'
        assert remaining_text == 'corporate governance process;'


        # reference_on_exclusion_list = 'Legal context'
        # indent, index, remaining_text = self.index_banking_act.parse_line_of_text(reference_on_exclusion_list)
        # assert indent == 0
        # assert index == 'Legal context'
        # assert remaining_text == ''

        # reference_on_exclusion_list_wrong_indent = '    Legal context'
        # with pytest.raises(ValueError):
        #     indent, index, remaining_text = self.index_banking_act.parse_line_of_text(reference_on_exclusion_list_wrong_indent)

        

    def test___extract_reference_from_string(self):
        string_with_no_reference = 'Africa means any country forming part of the African Union.'
        index, string = self.index_banking_act._extract_reference_from_string(string_with_no_reference)
        assert index == ""
        assert string == string_with_no_reference

        # tests for each of the numbering patters used in excon_index_patterns
        string_with_reference = '(1) Definitions'
        index, string = self.index_banking_act._extract_reference_from_string(string_with_reference)
        assert index == "(1)"
        assert string == 'Definitions'

        string_with_reference = '(a) a list of application numbers generated but not submitted to the Financial Surveillance Department;'
        index, string = self.index_banking_act._extract_reference_from_string(string_with_reference)
        assert index == "(a)"
        assert string == 'a list of application numbers generated but not submitted to the Financial Surveillance Department;'

        string_with_reference = '(xviii) Authorised Dealers must reset their application numbering systems to zero at the beginning of each calendar year.'
        index, string = self.index_banking_act._extract_reference_from_string(string_with_reference)
        assert index == "(xviii)"
        assert string == 'Authorised Dealers must reset their application numbering systems to zero at the beginning of each calendar year.'

        string_with_reference = '(A) Authorised Dealers'
        index, string = self.index_banking_act._extract_reference_from_string(string_with_reference)
        assert index == "(A)"
        assert string == 'Authorised Dealers'


        string_with_reference = '(dd) CMA residents who travel overland to and from other CMA countries through a SADC country up to an amount not exceeding R25 000 per calendar year. This allocation does not form part of the permissible travel allowance for residents; and'
        index, string = self.index_banking_act._extract_reference_from_string(string_with_reference)
        assert index == "(dd)"
        assert string == 'CMA residents who travel overland to and from other CMA countries through a SADC country up to an amount not exceeding R25 000 per calendar year. This allocation does not form part of the permissible travel allowance for residents; and'

        # heading_on_exclusion_list = 'Legal context'
        # index, string = self.index_banking_act._extract_reference_from_string(heading_on_exclusion_list)
        # assert index == heading_on_exclusion_list
        # assert string == ""
