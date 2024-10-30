from django.urls import path

from wallets.views.wallet_view import (
    WalletBalanceView,
    WalletRechargeView,
    WalletWithdrawView,
)

urlpatterns = [
    # 나의 지갑 (코인 갯수)
    path("coin/", WalletBalanceView.as_view(), name="user-coin-wallet"),
    # 코인 충전
    path("coin/recharge/", WalletRechargeView.as_view(), name="user-coin-recharge"),
    # 코인 차감
    path("coin/withdraw/", WalletWithdrawView.as_view(), name="user-coin-withdraw"),
]
