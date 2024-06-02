from sqlalchemy import Integer, String, Boolean, Date
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):


    """
    A model which represents a user in a database.

    Contains his id, names and scores.
    cur_scores is a count of scores which allow to spend on hits by command /spend.
    spent_scores is a count of scores which already was spent on hits by command /spend.
    """

    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    cur_scores: Mapped[int] = mapped_column(Integer)
    spent_scores: Mapped[int] = mapped_column(Integer)


class Image(Base):
    """
    A model which represents an image in a database.

    Contains image's id, user's id who sent it, date when it was uploaded by a command /upload.
    is_used is a flag which answer to a question "Has this image already showed when a user spent his score by
    a command /spend?" to not send the same image several times.
    """

    __tablename__ = "images"
    image_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    date: Mapped[date] = mapped_column(Date)
    is_used: Mapped[bool] = mapped_column(Boolean)


class UserManager:
    """
    This class manage operations with users.
    Add a user to a database, check his presence to a database, get and change user's attributes.
    """

    def __init__(self, db_engine, db_session) -> None:
        self.db_engine = db_engine
        self.db_session = db_session

    def add_user(
        self,
        user_id: int,
        username: str,
        first_name: str,
        last_name: str,
        cur_score: int = 0,
        used_score: int = 0,
    ) -> None:
        user = User(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            cur_scores=cur_score,
            spent_scores=used_score,
        )
        self.db_session.add(user)
        self.db_session.commit()

    def get_user(self, user_id: int):
        user = (
            self.db_session.execute(
                self.db_session.query(User).where(User.user_id == user_id)
            )
            .scalars()
            .all()
        )
        return False if len(user) == 0 else user[0]

    def increase_score(self, user_id: int):
        user: User = self.get_user(user_id)
        if user:
            user.cur_scores += 1
            self.db_session.commit()

    def decrease_score(self, user_id: int):
        user: User = self.get_user(user_id)
        if user and user.cur_scores > 0:
            user.cur_scores -= 1
            user.spent_scores += 1
            self.db_session.commit()

    def get_balance(self, user_id: int):
        user: User = self.get_user(user_id)
        if user:
            return [user.cur_scores, user.spent_scores]
        return []


class ImageManager:
    """
    This class manage operations with images.
    It can add images to a database and get them from there. Change image's attributes if an image has been used
    on a command /spend.
    """

    def __init__(self, db_engine, db_session):
        self.db_engine = db_engine
        self.db_session = db_session

    def add_image(self, image_id, user_id, date):
        image = Image(image_id=image_id, user_id=user_id, date=date, is_used=False)
        self.db_session.add(image)
        self.db_session.commit()

    def get_all_images(self, user_id):
        return (
            self.db_session.execute(
                self.db_session.query(Image).where(Image.user_id == user_id)
            )
            .scalars()
            .all()
        )

    def get_not_used_images(self, user_id):
        return (
            self.db_session.execute(
                self.db_session.query(Image).where(
                    (Image.user_id == user_id) & (Image.is_used == False)
                )
            )
            .scalars()
            .all()
        )

    def get_used(self, image: Image):
        image.is_used = True
        self.db_session.commit()

