import pytest
import time

@pytest.mark.api
def test_create_and_delete_board(rest_controller):
    board_name = f"api_test_board_{int(time.time())}"

    board_id = rest_controller.create_board(board_name)
    assert board_id is not None

    data, status = rest_controller.get_board_information()
    assert status == 200
    assert data.get("name") == board_name

    # cleanup
    rest_controller.delete_board()
