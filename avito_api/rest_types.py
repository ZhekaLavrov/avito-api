from datetime import datetime, date, timedelta

from pydantic import BaseModel, Field


class AccessToken(BaseModel):
    access_token: str
    expires_in: int
    token_type: str


class UserInfoSelf(BaseModel):
    email: str = ''
    id: int = 0
    name: str = ''
    phone: str = ''
    profile_url: str = ''


class AutoloadItemInfo(BaseModel):
    class FeeInfo(BaseModel):
        amount: int = ''
        package_id: int = ''
        type: str = ''

    class Message(BaseModel):
        code: int = ''
        description: str = ''
        title: str = ''
        type: str = ''
        updated_at: datetime = ''

    class Section(BaseModel):
        slug: str = ''
        title: str = ''

    ad_id: str
    avito_date_end: datetime = ''
    avito_id: int = ''
    avito_status: str = ''
    fee_info: FeeInfo = FeeInfo.parse_obj({})
    messages: list[Message] = []
    processing_time: datetime = ''
    section: Section = Section.parse_obj({})
    url: str = ''


class Ok(BaseModel):
    ok: bool


class ItemStatsShallow(BaseModel):
    class Stat(BaseModel):
        date: date
        uniq_views: int = Field(alias='uniqViews', default=0)
        uniq_contacts: int = Field(alias='uniqContacts', default=0)
        uniq_favorites: int = Field(alias='uniqFavorites', default=0)

    item_id: int = Field(alias='itemId')
    stats: list[Stat] = []


class ItemStatsShallowDay(ItemStatsShallow):
    def get_all_uniq_views(self) -> int:
        return sum([stat.uniq_views for stat in self.stats])

    def get_all_uniq_contacts(self) -> int:
        return sum([stat.uniq_contacts for stat in self.stats])

    def get_all_uniq_favorites(self) -> int:
        return sum([stat.uniq_favorites for stat in self.stats])

    def get_last_day_uniq_views(self) -> int:
        return self.stats[-1].uniq_views if self.stats and self.stats[-1].date == date.today() else 0

    def get_last_day_uniq_contacts(self) -> int:
        return self.stats[-1].uniq_contacts if self.stats and self.stats[-1].date == date.today() else 0

    def get_last_day_uniq_favorites(self) -> int:
        return self.stats[-1].uniq_favorites if self.stats and self.stats[-1].date == date.today() else 0


class ItemStatsShallowWeek(ItemStatsShallow):
    def get_last_week_uniq_views(self) -> int:
        return self.stats[-1].uniq_views if self.stats and self.stats[-1].date >= date.today() - timedelta(7) else 0

    def get_last_week_uniq_contacts(self) -> int:
        return self.stats[-1].uniq_contacts if self.stats and self.stats[-1].date >= date.today() - timedelta(7) else 0

    def get_last_week_uniq_favorites(self) -> int:
        return self.stats[-1].uniq_favorites if self.stats and self.stats[-1].date >= date.today() - timedelta(7) else 0


class ItemStatsShallowMonth(ItemStatsShallow):
    def get_last_month_uniq_views(self) -> int:
        return self.stats[-1].uniq_views if self.stats and self.stats[-1].date >= date.today() - timedelta(31) else 0

    def get_last_month_uniq_contacts(self) -> int:
        return self.stats[-1].uniq_contacts if self.stats and self.stats[-1].date >= date.today() - timedelta(31) else 0

    def get_last_month_uniq_favorites(self) -> int:
        s = self.stats
        return s[-1].uniq_favorites if s and s[-1].date >= date.today() - timedelta(31) else 0
