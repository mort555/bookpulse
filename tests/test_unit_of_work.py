from unittest.mock import MagicMock

import pytest
from app.infra.database.unit_of_work import SqlAlchemyUnitOfWork


def test_unit_of_work_commits_and_closes_session() -> None:
    session = MagicMock()
    uow = SqlAlchemyUnitOfWork(lambda: session)

    with uow:
        assert uow.session is session
        assert uow.suppliers is not None

    session.commit.assert_called_once()
    session.rollback.assert_not_called()
    session.close.assert_called_once()
    assert uow.session is None
    assert uow.suppliers is None


def test_unit_of_work_rolls_back_on_exception() -> None:
    session = MagicMock()
    uow = SqlAlchemyUnitOfWork(lambda: session)

    with pytest.raises(RuntimeError, match="test error"), uow:
        raise RuntimeError("test error")

    session.commit.assert_not_called()
    session.rollback.assert_called_once()
    session.close.assert_called_once()


def test_unit_of_work_closes_session_if_commit_fails() -> None:
    session = MagicMock()
    session.commit.side_effect = RuntimeError("commit failed")
    uow = SqlAlchemyUnitOfWork(lambda: session)

    with pytest.raises(RuntimeError, match="commit failed"), uow:
        pass

    session.commit.assert_called_once()
    session.close.assert_called_once()
