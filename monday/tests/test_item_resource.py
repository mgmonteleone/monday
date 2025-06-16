from monday.tests.test_case_resource import BaseTestCase
from monday.query_joins import mutate_item_query, get_item_query, update_item_query, get_item_by_id_query, \
    update_multiple_column_values_query, mutate_subitem_query, add_file_to_column_query, delete_item_query, \
    archive_item_query, move_item_to_group_query
from monday.utils import monday_json_stringify


class ItemTestCase(BaseTestCase):
    def setUp(self):
        super(ItemTestCase, self).setUp()

    def test_mutate_item_query(self):
        query = mutate_item_query(board_id=self.board_id, group_id=self.group_id, item_name=self.item_name,
                                  column_values=self.column_values, create_labels_if_missing=False)
        self.assertIn(str(self.board_id), query)
        self.assertIn(str(self.group_id), query)
        self.assertIn(self.item_name, query)
        self.assertIn(monday_json_stringify(self.column_values), query)
        self.assertNotIn("create_labels_if_missing: true", query)

    def test_get_item_query(self):
        query = get_item_query(board_id=self.board_id,
                               column_id=self.column_id, value="foo")
        self.assertIn(str(self.board_id), query)
        self.assertIn(self.column_id, query)
        self.assertIn("foo", query)
        # Test for our enhancements
        self.assertIn("board {", query)
        self.assertIn("id", query)
        self.assertIn("name", query)
        self.assertIn("column {", query)
        self.assertIn("title", query)

    def test_get_item_query_with_limit_and_cursor(self):
        limit = 10
        cursor = "MSw0NTc5ODYzMTkyLFRWX2ljOW..."
        query = get_item_query(board_id=self.board_id, column_id=None, value="foo", limit=limit, cursor=cursor)
        items_page_line = f'items_page_by_column_values (board_id: {self.board_id}, limit: {limit}, cursor: "{cursor}")'
        self.assertIn(items_page_line, query)
        self.assertNotIn(self.column_id, query)
        self.assertNotIn("foo", query)

    def test_update_item_query(self):
        query = update_item_query(
            board_id=self.board_id, item_id=self.item_id, column_id=self.column_id, value="foo")
        self.assertIn(str(self.board_id), query)
        self.assertIn(str(self.item_id), query)
        self.assertIn(self.column_id, query)
        self.assertIn("foo", query)
        # Test for our enhancements
        self.assertIn("board {", query)
        self.assertIn("column {", query)
        self.assertIn("title", query)

    def test_get_item_by_id_query(self):
        query = get_item_by_id_query(ids=self.item_id)
        self.assertIn(str(self.item_id), query)
        # Test for our enhancements
        self.assertIn("board {", query)
        self.assertIn("column {", query)
        self.assertIn("title", query)

    def test_update_multiple_column_values(self):
        query = update_multiple_column_values_query(board_id=self.board_id, item_id=self.item_id,
                                                    column_values=self.column_values, create_labels_if_missing=False)
        self.assertIn(str(self.board_id), query)
        self.assertIn(str(self.item_id), query)
        self.assertIn(monday_json_stringify(self.column_values), query)
        self.assertNotIn("create_labels_if_missing: true", query)
        # Test for our enhancements
        self.assertIn("board {", query)
        self.assertIn("column {", query)
        self.assertIn("title", query)

    def test_mutate_subitem_query(self):
        query = mutate_subitem_query(parent_item_id=self.item_id, subitem_name=self.subitem_name, column_values=None,
                                     create_labels_if_missing=False)
        self.assertIn(str(self.item_id), query)
        self.assertIn(self.subitem_name, query)
        self.assertNotIn("create_labels_if_missing: true", query)

    def test_add_file_to_column_query(self):
        query = add_file_to_column_query(
            item_id=self.item_id, column_id=self.column_id)
        self.assertIn(str(self.item_id), query)
        self.assertIn(str(self.column_id), query)

    def test_delete_item_by_id(self):
        query = delete_item_query(item_id=self.item_id)
        self.assertIn(str(self.item_id), query)
        self.assertEqual('''
        mutation
        {
            delete_item (item_id: 24)
            {
                id
            }
        }'''.replace(" ", ""), query.replace(" ", ""))
        
    def test_archive_item_by_id(self):
        query = archive_item_query(item_id=self.item_id)
        self.assertIn(str(self.item_id), query)
        self.assertEqual('''
        mutation
        {
            archive_item (item_id: 24)
            {
                id
            }
        }'''.replace(" ", ""), query.replace(" ", ""))

    def test_move_item_to_group_query(self):
        query = move_item_to_group_query(item_id=self.item_id, group_id=self.group_id)
        self.assertIn(str(self.item_id), query)
        self.assertIn(str(self.group_id), query)

    # New comprehensive tests for our v2.0.2 enhancements
    def test_get_item_query_contains_board_information(self):
        """Test that get_item_query includes board { id, name } in the response"""
        query = get_item_query(board_id=self.board_id, column_id=self.column_id, value="test")
        
        # Verify exact board structure
        self.assertIn("board {", query)
        self.assertIn("id", query)
        self.assertIn("name", query)
        
        # Verify board block is properly structured
        board_section = query[query.find("board {"):query.find("}", query.find("board {")) + 1]
        self.assertIn("id", board_section)
        self.assertIn("name", board_section)

    def test_get_item_query_contains_column_titles(self):
        """Test that get_item_query includes column { title } in column_values"""
        query = get_item_query(board_id=self.board_id, column_id=self.column_id, value="test")
        
        # Verify column title structure
        self.assertIn("column_values {", query)
        self.assertIn("column {", query)
        self.assertIn("title", query)
        
        # Ensure both enhancements are present
        column_values_start = query.find("column_values {")
        column_values_end = query.find("}", query.rfind("column_values {"))
        column_values_section = query[column_values_start:column_values_end]
        self.assertIn("column {", column_values_section)
        self.assertIn("title", column_values_section)

    def test_get_item_by_id_query_enhancements(self):
        """Test that get_item_by_id_query includes both board and column title info"""
        query = get_item_by_id_query(ids=[self.item_id, 999])
        
        # Board information
        self.assertIn("board {", query)
        board_section = query[query.find("board {"):query.find("}", query.find("board {")) + 1]
        self.assertIn("id", board_section)
        self.assertIn("name", board_section)
        
        # Column titles
        self.assertIn("column_values {", query)
        self.assertIn("column {", query)
        column_values_section = query[query.find("column_values {"):]
        self.assertIn("column {", column_values_section)
        self.assertIn("title", column_values_section)

    def test_update_item_query_enhancements(self):
        """Test that update_item_query returns board and column info in response"""
        query = update_item_query(board_id=self.board_id, item_id=self.item_id, 
                                 column_id=self.column_id, value={"index": 1})
        
        # Verify mutation response includes board info
        self.assertIn("board {", query)
        self.assertIn("column_values {", query)
        self.assertIn("column {", query)
        self.assertIn("title", query)

    def test_update_multiple_column_values_enhancements(self):
        """Test that update_multiple_column_values_query includes our enhancements"""
        query = update_multiple_column_values_query(board_id=self.board_id, item_id=self.item_id,
                                                   column_values=self.column_values, 
                                                   create_labels_if_missing=True)
        
        # Board information in response
        self.assertIn("board {", query)
        # Column titles in response
        self.assertIn("column {", query)
        self.assertIn("title", query)
        # Should also include create_labels_if_missing: true
        self.assertIn("create_labels_if_missing: true", query)

    def test_all_item_queries_have_consistent_enhancements(self):
        """Test that all our enhanced queries have consistent structure"""
        queries = [
            get_item_query(board_id=self.board_id, column_id=self.column_id, value="test"),
            get_item_by_id_query(ids=[self.item_id]),
            update_item_query(board_id=self.board_id, item_id=self.item_id, 
                             column_id=self.column_id, value="test"),
            update_multiple_column_values_query(board_id=self.board_id, item_id=self.item_id,
                                               column_values=self.column_values)
        ]
        
        for i, query in enumerate(queries):
            with self.subTest(f"Query {i}"):
                # Every enhanced query should have board info
                self.assertIn("board {", query, f"Query {i} missing board info")
                # Every enhanced query should have column titles
                self.assertIn("column {", query, f"Query {i} missing column titles")
                self.assertIn("title", query, f"Query {i} missing title field")
