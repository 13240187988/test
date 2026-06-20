import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random

st.set_page_config(page_title="上证指数月线模拟交易", page_icon="📈", layout="wide")


@st.cache_data
def load_data():
    data = {
        '交易时间': ['2007-01-31', '2007-02-28', '2007-03-30', '2007-04-30', '2007-05-31', '2007-06-29', '2007-07-31',
                     '2007-08-31', '2007-09-28', '2007-10-31', '2007-11-30', '2007-12-28', '2008-01-31', '2008-02-29',
                     '2008-03-31', '2008-04-30', '2008-05-30', '2008-06-30', '2008-07-31', '2008-08-29', '2008-09-26',
                     '2008-10-31', '2008-11-28', '2008-12-31', '2009-01-23', '2009-02-27', '2009-03-31', '2009-04-30',
                     '2009-05-27'],
        '收盘价': [2786.33, 2881.07, 3183.98, 3841.27, 4109.65, 3820.70, 4471.03, 5218.83, 5552.30, 5954.77, 4871.78,
                   5261.56, 4383.39, 4348.54, 3472.71, 3693.11, 3433.35, 2736.10, 2775.72, 2397.37, 2293.78, 1728.79,
                   1871.16, 1820.81, 1990.66, 2082.85, 2373.21, 2477.57, 2632.93],
        '涨跌幅%': [4.1436, 3.4002, 10.5138, 20.6437, 6.9868, -7.031, 17.0212, 16.7255, 6.3897, 7.2487, -18.1869,
                    8.0008, -16.6903, -0.795, -20.1408, 6.3466, -7.0336, -20.3082, 1.448, -13.6307, -4.321, -24.6314,
                    8.2352, -2.6908, 9.3283, 4.6311, 13.9405, 4.3974, 6.2707]
    }
    df = pd.DataFrame(data)
    df['交易时间'] = pd.to_datetime(df['交易时间'])
    return df


def init_state():
    if 'step' not in st.session_state:
        st.session_state.step = 0
        st.session_state.holdings = True
        st.session_state.cash = 100000
        st.session_state.shares = int(100000 / 2786.33 * 100) / 100
        st.session_state.buy_price = 2786.33
        st.session_state.records = []
        st.session_state.game_over = False
        st.session_state.show_balloons = False
        st.session_state.early_settle = False  # 是否提前结算


def get_current_data(df):
    if st.session_state.step < len(df):
        return df.iloc[st.session_state.step]
    return None


def get_next_data(df):
    if st.session_state.step + 1 < len(df):
        return df.iloc[st.session_state.step + 1]
    return None


def calculate_total_asset(current_price):
    if st.session_state.holdings:
        return st.session_state.shares * current_price
    return st.session_state.cash


def generate_comment(action, next_row):
    if next_row is None:
        return "🎉 模拟结束！"
    change = next_row['涨跌幅%']
    month = next_row['交易时间'].strftime('%Y年%m月')

    if action == "持有":
        if change > 0:
            msgs = [f"🎯 明智之举！{month}上涨{change:.2f}%，朋友们都羡慕你！",
                    f"🚀 股神附体！{month}大涨{change:.2f}%，你已成传说！", f"💰 精准判断！{month}涨了{change:.2f}%，加鸡腿！",
                    f"🏆 太强了！{month}上涨{change:.2f}%，财富神话！"]
        else:
            msgs = [f"😅 有点可惜！{month}跌了{change:.2f}%，好戏在后头！",
                    f"🤔 市场无情！{month}下跌{change:.2f}%，机会在下跌中孕育！",
                    f"📉 暂时回调！{month}跌了{change:.2f}%，黎明在前方！",
                    f"💪 风雨过后见彩虹！{month}跌了{change:.2f}%，勇气可嘉！"]

    elif action == "卖出":
        if change > 0:
            msgs = [f"😱 卖飞了！{month}大涨{change:.2f}%，朋友们笑你太急！",
                    f"😭 拍断大腿！{month}涨了{change:.2f}%，本可赚更多！",
                    f"🤦 操之过急！{month}上涨{change:.2f}%，再等等就好了！",
                    f"😤 被教育了！{month}涨{change:.2f}%，卖出的代价！"]
        else:
            msgs = [f"🛡️ 避险成功！{month}大跌{change:.2f}%，躲过一劫！", f"🧠 高手风范！{month}跌了{change:.2f}%，空仓明智！",
                    f"💡 未雨绸缪！{month}下跌{change:.2f}%，判断精准！", f"🌟 大师级别！{month}跌了{change:.2f}%，满分操作！"]

    elif action == "买入":
        if change > 0:
            msgs = [f"🚀 抄底成功！{month}大涨{change:.2f}%，精准入场！", f"💰 眼光独到！{month}涨了{change:.2f}%，低位建仓！",
                    f"🎯 完美时机！{month}上涨{change:.2f}%，高手！"]
        else:
            msgs = [f"😅 买早了！{month}跌了{change:.2f}%，但机会是等出来的！",
                    f"📉 暂时被套！{month}下跌{change:.2f}%，坚守价值！",
                    f"💪 逆向投资！{month}跌了{change:.2f}%，你是勇敢者！"]

    else:  # 空仓观望
        if change > 0:
            msgs = [f"😭 踏空了！{month}大涨{change:.2f}%，你在场外观望！",
                    f"🤔 太保守了！{month}涨了{change:.2f}%，错过一波行情！",
                    f"😅 看着别人赚钱！{month}上涨{change:.2f}%，你选择了观望！",
                    f"💔 遗憾！{month}涨{change:.2f}%，空仓的代价！"]
        else:
            msgs = [f"🛡️ 完美避险！{month}大跌{change:.2f}%，空仓让你躲过一劫！",
                    f"🧠 大师风范！{month}跌了{change:.2f}%，耐心等待是美德！",
                    f"💡 明智之选！{month}下跌{change:.2f}%，现金为王！",
                    f"🌟 防守大师！{month}跌了{change:.2f}%，你保住了本金！"]

    return random.choice(msgs)


def handle_action(action, df):
    current = get_current_data(df)
    if current is None:
        return
    price = current['收盘价']
    change = current['涨跌幅%']
    month = current['交易时间'].strftime('%Y-%m')

    if action == "持有":
        pass
    elif action == "卖出":
        st.session_state.cash = st.session_state.shares * price
        st.session_state.shares = 0
        st.session_state.holdings = False
    elif action == "买入":
        st.session_state.shares = st.session_state.cash / price
        st.session_state.buy_price = price
        st.session_state.cash = 0
        st.session_state.holdings = True
    elif action == "空仓观望":
        pass

    next_row = get_next_data(df)
    comment = generate_comment(action, next_row)
    st.session_state.records.append({'月份': month, '收盘价': price, '涨跌幅': change, '操作': action, '评价': comment})
    st.session_state.step += 1
    if st.session_state.step >= len(df):
        st.session_state.game_over = True
        st.session_state.show_balloons = True


def early_settle(df):
    """提前结算：按当前价格清仓，结束游戏"""
    current = get_current_data(df)
    if current is not None:
        price = current['收盘价']
        # 如果持有股票，先清仓
        if st.session_state.holdings:
            st.session_state.cash = st.session_state.shares * price
            st.session_state.shares = 0
            st.session_state.holdings = False
        st.session_state.game_over = True
        st.session_state.show_balloons = True
        st.session_state.early_settle = True

        # 添加一条结算记录
        st.session_state.records.append({
            '月份': current['交易时间'].strftime('%Y-%m'),
            '收盘价': price,
            '涨跌幅': current['涨跌幅%'],
            '操作': '💼 提前结算',
            '评价': f"📊 在第 {st.session_state.step + 1} 个月选择落袋为安！"
        })


def reset_game():
    st.session_state.step = 0
    st.session_state.holdings = True
    st.session_state.cash = 100000
    st.session_state.shares = int(100000 / 2786.33 * 100) / 100
    st.session_state.buy_price = 2786.33
    st.session_state.records = []
    st.session_state.game_over = False
    st.session_state.show_balloons = False
    st.session_state.early_settle = False


def get_final_comment(final_rate):
    if final_rate > 50:
        return "🏆 也就那样吧，赶上了风口而已！"
    elif final_rate > 30:
        return "🌟 优秀！投资眼光不错！"
    elif final_rate > 10:
        return "👍 稳健，但是你没抓住这波机会，您身边朋友都资产翻倍了！"
    elif final_rate > 0:
        return "📈 不是，这牛市，你才赚这么点？存银行去吧"
    elif final_rate > -10:
        return "😅 谁让你不止损的，哈哈哈"
    elif final_rate > -30:
        return "😰 完蛋了吧，让你不见好就收"
    else:
        return "💀 看你怎么和家人交代！！"


def main():
    init_state()
    df = load_data()
    st.title("📈 上证指数月线模拟交易")
    st.markdown("从2007年1月到2009年5月，共29个月，根据每月行情决定买入/持有/卖出/空仓")

    with st.sidebar:
        st.header("📊 账户信息")
        current = get_current_data(df)
        if current is not None and not st.session_state.game_over:
            price = current['收盘价']
            total = calculate_total_asset(price)
            profit = total - 100000
            rate = (profit / 100000) * 100
            st.metric("💰 总资产", f"¥{total:,.2f}")
            st.metric("📈 总盈亏", f"¥{profit:,.2f}", delta=f"{rate:.2f}%")
            status = "📦 持有" if st.session_state.holdings else "💵 空仓"
            st.info(f"状态: {status}")
            if st.session_state.holdings:
                st.info(f"买入价: ¥{st.session_state.buy_price:.2f}")
            st.info(f"📅 第 {st.session_state.step + 1}/{len(df)} 个月")
        elif st.session_state.game_over:
            # 结算后显示最终结果
            final_price = df.iloc[-1]['收盘价'] if not st.session_state.early_settle else current[
                '收盘价'] if current is not None else df.iloc[-1]['收盘价']
            final_asset = calculate_total_asset(
                final_price) if not st.session_state.game_over else st.session_state.cash
            if st.session_state.early_settle:
                final_asset = st.session_state.cash
            profit = final_asset - 100000
            rate = (profit / 100000) * 100
            st.metric("💰 最终资产", f"¥{final_asset:,.2f}")
            st.metric("📈 最终盈亏", f"¥{profit:,.2f}", delta=f"{rate:.2f}%")
            if st.session_state.early_settle:
                st.info(f"⏰ 提前结算于第 {st.session_state.step} 个月")
            else:
                st.info("🏁 走完全程")

        st.markdown("---")
        if st.button("🔄 重新开始", use_container_width=True):
            reset_game()
            st.rerun()

    col1, col2 = st.columns([2, 1])
    with col1:
        fig = go.Figure()

        if st.session_state.step >= 0:
            hist = df.iloc[:st.session_state.step + 1]
            fig.add_trace(go.Scatter(
                x=hist['交易时间'],
                y=hist['收盘价'],
                mode='lines+markers',
                name='📈 历史走势',
                line=dict(color='#1f77b4', width=2.5),
                marker=dict(size=8, color='#1f77b4')
            ))

        if current is not None and not st.session_state.game_over:
            fig.add_trace(go.Scatter(
                x=[current['交易时间']],
                y=[current['收盘价']],
                mode='markers',
                name='📍 当前位置',
                marker=dict(size=20, color='red', symbol='star')
            ))

        # 如果提前结算，标记结算点
        if st.session_state.game_over and st.session_state.early_settle and current is not None:
            fig.add_trace(go.Scatter(
                x=[current['交易时间']],
                y=[current['收盘价']],
                mode='markers',
                name='💼 结算点',
                marker=dict(size=22, color='gold', symbol='diamond')
            ))

        fig.update_layout(
            title='上证指数月线走势',
            xaxis_title='时间',
            yaxis_title='收盘价',
            height=420,
            hovermode='x',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
            xaxis=dict(range=[df['交易时间'].min(), df['交易时间'].max()])
        )
        st.plotly_chart(fig, use_container_width=True)
        if not st.session_state.game_over:
            st.caption(
                f"已走过 {st.session_state.step + 1}/{len(df)} 个月，剩余 {len(df) - st.session_state.step - 1} 个月未知")
        else:
            if st.session_state.early_settle:
                st.caption(f"💼 提前结算于第 {st.session_state.step} 个月")
            else:
                st.caption("🏁 走完全程！")

    with col2:
        st.subheader("🎯 操作区")

        if st.session_state.game_over:
            st.success("🏁 游戏已结束！")
            final_price = df.iloc[-1]['收盘价'] if not st.session_state.early_settle else current[
                '收盘价'] if current is not None else df.iloc[-1]['收盘价']
            final_asset = st.session_state.cash if st.session_state.early_settle else calculate_total_asset(final_price)
            final_profit = final_asset - 100000
            final_rate = (final_profit / 100000) * 100

            st.metric("最终资产", f"¥{final_asset:,.2f}")
            st.metric("总盈亏", f"¥{final_profit:,.2f}", delta=f"{final_rate:.2f}%")

            st.markdown("---")
            comment = get_final_comment(final_rate)
            if final_rate > 0:
                st.success(f"{comment}")
            else:
                st.warning(f"{comment}")

            if st.session_state.early_settle:
                st.info(f"⏰ 你在第 {st.session_state.step} 个月选择提前结算，落袋为安！")
            else:
                st.info("📊 你走完了全部29个月！")

            if st.session_state.show_balloons:
                st.balloons()
                st.session_state.show_balloons = False

        elif current is not None:
            st.write(f"**{current['交易时间'].strftime('%Y年%m月')}**")
            st.write(f"收盘价: **{current['收盘价']:.2f}**")
            change = current['涨跌幅%']
            color = "green" if change >= 0 else "red"
            st.write(f"涨跌幅: **<span style='color:{color}'>{change:.2f}%</span>**", unsafe_allow_html=True)
            st.markdown("---")

            # 操作按钮
            if st.session_state.holdings:
                st.info("📦 当前持有股票")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ 继续持有", use_container_width=True):
                        handle_action("持有", df)
                        st.rerun()
                with c2:
                    if st.button("💸 卖出离场", use_container_width=True):
                        handle_action("卖出", df)
                        st.rerun()
            else:
                st.info("💵 当前空仓")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("📈 买入建仓", use_container_width=True):
                        handle_action("买入", df)
                        st.rerun()
                with c2:
                    if st.button("⏸️ 继续空仓", use_container_width=True):
                        handle_action("空仓观望", df)
                        st.rerun()

            st.markdown("---")
            # 提前结算按钮（危险操作）
            if st.button("💼 提前结算（落袋为安）", use_container_width=True, type="secondary"):
                early_settle(df)
                st.rerun()
            st.caption("⚠️ 点击后将按当前价格清仓并结束游戏")

    st.markdown("---")
    st.subheader("📝 交易记录与评价")
    if st.session_state.records:
        for r in st.session_state.records:
            op = r['操作']
            if op == "持有":
                st.info(f"📅 {r['月份']} | 操作: {op} | 涨跌: {r['涨跌幅']:.2f}% | {r['评价']}")
            elif op == "卖出":
                st.warning(f"📅 {r['月份']} | 操作: {op} | 涨跌: {r['涨跌幅']:.2f}% | {r['评价']}")
            elif op == "买入":
                st.success(f"📅 {r['月份']} | 操作: {op} | 涨跌: {r['涨跌幅']:.2f}% | {r['评价']}")
            elif op == "空仓观望":
                st.info(f"📅 {r['月份']} | 操作: {op} | 涨跌: {r['涨跌幅']:.2f}% | {r['评价']}")
            else:  # 提前结算
                st.success(f"📅 {r['月份']} | {op} | {r['评价']}")
    else:
        st.info("还没有交易记录，开始你的投资之旅吧！")


if __name__ == "__main__":
    main()