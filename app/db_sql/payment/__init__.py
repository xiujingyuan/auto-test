from app.common.db_class import DataBase
from app.common.tools import CheckExist


class PaymentDbBase(DataBase):

    def __init__(self, num, country, env):
        super(PaymentDbBase, self).__init__('payment', num, country, env)

    @CheckExist()
    def get_asset_by_item_no(self, item_no):
        asset = self.get_data('asset', asset_item_no=item_no)
        return asset
