import typer
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.database import create_db_and_tables, drop_all, get_session
from app.models import User

cli = typer.Typer()


@cli.command()
def initialize():
    with get_session() as db:  # Get a connection to the database
        drop_all()  # delete all tables
        create_db_and_tables()  # recreate all tables
        bob = User('bob', 'bob@mail.com', 'bobpass')  # Create a new user (in memory)
        db.add(bob)  # Tell the database about this new data
        db.commit()  # Tell the database persist the data
        db.refresh(bob)  # Update the user (we use this to get the ID from the db)
        print("Database Initialized")


@cli.command()
def get_user(
    username: str = typer.Argument(..., help="The username to find.")
):
    with get_session() as db:  # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found!')
            return
        print(user)


@cli.command()
def find_user(
    search_term: str = typer.Argument(..., help="Part of a username or email.")
):
    with get_session() as db:
        users = db.exec(
            select(User).where(
                or_(
                    User.username.ilike(f"%{search_term}%"),
                    User.email.ilike(f"%{search_term}%")
                )
            )
        ).all()
        if not users:
            print(f'No users found matching "{search_term}"')
            return
        for user in users:
            print(user)


@cli.command()
def get_all_users():
    with get_session() as db:
        all_users = db.exec(select(User)).all()
        if not all_users:
            print("No users found")
        else:
            for user in all_users:
                print(user)


@cli.command()
def list_users(
    limit: int = typer.Argument(10, help="How many users to show."),
    offset: int = typer.Argument(0, help="How many users to skip.")
):
    with get_session() as db:
        users = db.exec(select(User).offset(offset).limit(limit)).all()
        if not users:
            print("No users found")
            return
        for user in users:
            print(user)


@cli.command()
def change_email(
    username: str = typer.Argument(..., help="The username to update."),
    new_email: str = typer.Argument(..., help="The new email.")
):
    with get_session() as db:  # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to update email.')
            return
        user.email = new_email
        db.add(user)
        db.commit()
        print(f"Updated {user.username}'s email to {user.email}")


@cli.command()
def create_user(
    username: str = typer.Argument(..., help="The username for the new user."),
    email: str = typer.Argument(..., help="The email for the new user."),
    password: str = typer.Argument(..., help="The password for the new user.")
):
    with get_session() as db:  # Get a connection to the database
        newuser = User(username, email, password)
        try:
            db.add(newuser)
            db.commit()
            db.refresh(newuser)
        except IntegrityError:
            db.rollback()  # let the database undo any previous steps of a transaction
            print("Username or email already taken!")  # give the user a useful message
        else:
            print(newuser)  # print the newly created user


@cli.command()
def delete_user(
    username: str = typer.Argument(..., help="The username to delete.")
):
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to delete user.')
            return
        db.delete(user)
        db.commit()
        print(f'{username} deleted')


if __name__ == "__main__":
    cli()
