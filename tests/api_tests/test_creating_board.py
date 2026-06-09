import pytest
from helpers.data_gen import generate_random_name


@pytest.mark.api
def test_create_update_and_delete_board(rest_controller):

    board_name = "Board_" + str(generate_random_name())
    board_id = rest_controller.create_board(board_name)
    rest_controller.check_board_name_and_desc(board_id, board_name)

    changed_board_name, changed_board_desc = rest_controller.update_board(board_id, "Test name", "Test desc")
    rest_controller.check_board_name_and_desc(board_id, changed_board_name, changed_board_desc)

    rest_controller.delete_board(board_id)
    rest_controller.check_if_board_has_been_deleted(board_id, board_name)
