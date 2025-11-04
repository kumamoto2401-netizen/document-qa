from collections import defaultdict
import streamlit as st
import altair as alt
import pandas as pd
from st_supabase_connection import SupabaseConnection # Supabase接続ライブラリをインポート

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title="Inventory tracker",
    page_icon=":shopping_bags:",  # This is an emoji shortcode. Could be a URL too.
)


# -----------------------------------------------------------------------------
# Declare some useful functions.

# Supabase接続を確立
# secrets.tomlの [connections.supabase] セクションを参照
def get_supabase_conn():
    """Establishes connection to the Supabase database using st.connection."""
    try:
        # st.connectionを使用してSupabase接続を取得
        conn = st.connection("supabase", type=SupabaseConnection)
        return conn
    except Exception as e:
        st.error(f"Error connecting to Supabase. Check your secrets.toml file and network: {e}")
        return None


def initialize_data(conn):
    """Initializes the inventory table with some data (for first-time setup)."""
    # NOTE: In a real-world scenario with Supabase, you would typically
    # run an initial SQL script or migration tool to create the table and
    # insert initial data, as this function would only run once.
    # We keep the structure for completeness, assuming 'inventory' table exists.

    # Data to insert
    initial_inventory_data = [
        # Beverages
        {'item_name': 'Bottled Water (500ml)', 'price': 1.50, 'units_sold': 115, 'units_left': 15, 'cost_price': 0.80, 'reorder_point': 16, 'description': 'Hydrating bottled water'},
        {'item_name': 'Soda (355ml)', 'price': 2.00, 'units_sold': 93, 'units_left': 8, 'cost_price': 1.20, 'reorder_point': 10, 'description': 'Carbonated soft drink'},
        {'item_name': 'Energy Drink (250ml)', 'price': 2.50, 'units_sold': 12, 'units_left': 18, 'cost_price': 1.50, 'reorder_point': 8, 'description': 'High-caffeine energy drink'},
        {'item_name': 'Coffee (hot, large)', 'price': 2.75, 'units_sold': 11, 'units_left': 14, 'cost_price': 1.80, 'reorder_point': 5, 'description': 'Freshly brewed hot coffee'},
        {'item_name': 'Juice (200ml)', 'price': 2.25, 'units_sold': 11, 'units_left': 9, 'cost_price': 1.30, 'reorder_point': 5, 'description': 'Fruit juice blend'},

        # Snacks
        {'item_name': 'Potato Chips (small)', 'price': 2.00, 'units_sold': 34, 'units_left': 16, 'cost_price': 1.00, 'reorder_point': 10, 'description': 'Salted and crispy potato chips'},
        {'item_name': 'Candy Bar', 'price': 1.50, 'units_sold': 6, 'units_left': 19, 'cost_price': 0.80, 'reorder_point': 15, 'description': 'Chocolate and candy bar'},
        {'item_name': 'Granola Bar', 'price': 2.25, 'units_sold': 3, 'units_left': 12, 'cost_price': 1.30, 'reorder_point': 8, 'description': 'Healthy and nutritious granola bar'},
        {'item_name': 'Cookies (pack of 6)', 'price': 2.50, 'units_sold': 8, 'units_left': 8, 'cost_price': 1.50, 'reorder_point': 5, 'description': 'Soft and chewy cookies'},
        {'item_name': 'Fruit Snack Pack', 'price': 1.75, 'units_sold': 5, 'units_left': 10, 'cost_price': 1.00, 'reorder_point': 8, 'description': 'Assortment of dried fruits and nuts'},

        # Personal Care
        {'item_name': 'Toothpaste', 'price': 3.50, 'units_sold': 1, 'units_left': 9, 'cost_price': 2.00, 'reorder_point': 5, 'description': 'Minty toothpaste for oral hygiene'},
        {'item_name': 'Hand Sanitizer (small)', 'price': 2.00, 'units_sold': 2, 'units_left': 13, 'cost_price': 1.20, 'reorder_point': 8, 'description': 'Small sanitizer bottle for on-the-go'},
        {'item_name': 'Pain Relievers (pack)', 'price': 5.00, 'units_sold': 1, 'units_left': 5, 'cost_price': 3.00, 'reorder_point': 3, 'description': 'Over-the-counter pain relief medication'},
        {'item_name': 'Bandages (box)', 'price': 3.00, 'units_sold': 0, 'units_left': 10, 'cost_price': 2.00, 'reorder_point': 5, 'description': 'Box of adhesive bandages for minor cuts'},
        {'item_name': 'Sunscreen (small)', 'price': 5.50, 'units_sold': 6, 'units_left': 5, 'cost_price': 3.50, 'reorder_point': 3, 'description': 'Small bottle of sunscreen for sun protection'},

        # Household
        {'item_name': 'Batteries (AA, pack of 4)', 'price': 4.00, 'units_sold': 1, 'units_left': 5, 'cost_price': 2.50, 'reorder_point': 3, 'description': 'Pack of 4 AA batteries'},
        {'item_name': 'Light Bulbs (LED, 2-pack)', 'price': 6.00, 'units_sold': 3, 'units_left': 3, 'cost_price': 4.00, 'reorder_point': 2, 'description': 'Energy-efficient LED light bulbs'},
        {'item_name': 'Trash Bags (small, 10-pack)', 'price': 3.00, 'units_sold': 5, 'units_left': 10, 'cost_price': 2.00, 'reorder_point': 5, 'description': 'Small trash bags for everyday use'},
        {'item_name': 'Paper Towels (single roll)', 'price': 2.50, 'units_sold': 3, 'units_left': 8, 'cost_price': 1.50, 'reorder_point': 5, 'description': 'Single roll of paper towels'},
        {'item_name': 'Multi-Surface Cleaner', 'price': 4.50, 'units_sold': 2, 'units_left': 5, 'cost_price': 3.00, 'reorder_point': 3, 'description': 'All-purpose cleaning spray'},

        # Others
        {'item_name': 'Lottery Tickets', 'price': 2.00, 'units_sold': 17, 'units_left': 20, 'cost_price': 1.50, 'reorder_point': 10, 'description': 'Assorted lottery tickets'},
        {'item_name': 'Newspaper', 'price': 1.50, 'units_sold': 22, 'units_left': 20, 'cost_price': 1.00, 'reorder_point': 5, 'description': 'Daily newspaper'}
    ]

    try:
        # テーブルにデータを挿入。
        # idはSupabaseが自動採番すると仮定し、id列は除外。
        conn.client.table("inventory").insert(initial_inventory_data).execute()
        st.toast("Initial data inserted into Supabase. (Note: Only runs once)")
    except Exception as e:
        # 既にデータがある場合や、テーブルが存在しない場合にエラーになる可能性あり
        st.warning(f"Could not insert initial data (maybe data already exists?): {e}")


@st.cache_data(ttl=600)
def load_data(conn):
    """Loads the inventory data from the Supabase table."""
    try:
        # Supabaseの'inventory'テーブルから全てのデータを取得
        response = conn.client.table("inventory").select("*").execute()
        data = response.data
    except Exception as e:
        st.error(f"Error loading data from Supabase: {e}")
        return pd.DataFrame() # 空のDataFrameを返す

    # idがPostgresのSERIAL型などで自動採番されていると仮定
    df = pd.DataFrame(data)

    # DataFrameが空でないことを確認
    if not df.empty and 'id' in df.columns:
        # データベースから取得した'id'列がint型であることを保証
        df['id'] = df['id'].astype(int)

    return df


def update_data(conn, df, changes):
    """Updates the inventory data in the Supabase table."""

    # 1. 編集された行の更新
    if changes["edited_rows"]:
        deltas = st.session_state.inventory_table["edited_rows"]
        
        for i, delta in deltas.items():
            # 変更された行のidを取得
            item_id = int(df.loc[i, "id"]) 
            # deltaには変更された列のみが含まれるので、idでフィルタして更新
            try:
                conn.client.table("inventory").update(delta).eq("id", item_id).execute()
            except Exception as e:
                st.error(f"Error updating row ID {item_id}: {e}")

    # 2. 追加された行の挿入
    if changes["added_rows"]:
        # Supabaseに挿入するデータから'id'（自動採番を期待）を除外
        rows_to_insert = [
            {k: v for k, v in row.items() if k != 'id'}
            for row in changes["added_rows"]
        ]
        try:
            conn.client.table("inventory").insert(rows_to_insert).execute()
        except Exception as e:
            st.error(f"Error inserting new rows: {e}")

    # 3. 削除された行の削除
    if changes["deleted_rows"]:
        # 削除された行のIDリストを作成
        deleted_ids = [int(df.loc[i, "id"]) for i in changes["deleted_rows"]]
        try:
            # IDリストに含まれる全ての行を削除
            conn.client.table("inventory").delete().in_("id", deleted_ids).execute()
        except Exception as e:
            st.error(f"Error deleting rows with IDs {deleted_ids}: {e}")

    # キャッシュをクリアしてデータを再ロード
    st.cache_data.clear()
    st.toast("Changes committed to Supabase!")
    # Streamlitを再実行して最新データを表示
    st.experimental_rerun()


# -----------------------------------------------------------------------------
# Draw the actual page, starting with the inventory table.

# Set the title that appears at the top of the page.
"""
# :shopping_bags: Inventory tracker

**Welcome to Alice's Corner Store's intentory tracker!**
This page reads and writes directly from/to our inventory database (Supabase).
"""

st.info(
    """
    Use the table below to add, remove, and edit items.
    And don't forget to commit your changes when you're done.
    """
)

# Connect to database
conn = get_supabase_conn()

# NOTE: 初期データ挿入処理は、Supabaseを使用する場合、通常は
# データベースのセットアップ時に手動で一度だけ行われるべきです。
# 開発・テスト用に、もしテーブルが空であれば初期データを挿入する例を
# 意図的に省略するか、コメントアウトしておくことを推奨します。
# 以下の行は、一度Supabaseのコンソールで実行するか、
# アプリケーション初回起動時にのみ実行されるようにする必要があります。
# if conn:
#    # テーブルが空かどうかチェックし、空なら初期化データを入れる（ここでは単純化のためスキップ）
#    pass

# Load data from database
if conn:
    df = load_data(conn)
else:
    # 接続失敗時は空のDataFrameで続行
    df = pd.DataFrame(columns=[
            "id", "item_name", "price", "units_sold", "units_left", 
            "cost_price", "reorder_point", "description"
    ])


# Display data with editable table
edited_df = st.data_editor(
    df,
    disabled=["id"],  # Don't allow editing the 'id' column.
    num_rows="dynamic",  # Allow appending/deleting rows.
    column_config={
        # Show dollar sign before price columns.
        "price": st.column_config.NumberColumn(format="$%.2f"),
        "cost_price": st.column_config.NumberColumn(format="$%.2f"),
        # 'id'列が数値型として扱われるようにする
        "id": st.column_config.NumberColumn(format="%d"), 
    },
    key="inventory_table",
)

has_uncommitted_changes = any(len(v) for v in st.session_state.inventory_table.values())

st.button(
    "Commit changes",
    type="primary",
    disabled=not has_uncommitted_changes,
    # Update data in database
    on_click=update_data,
    args=(conn, df, st.session_state.inventory_table),
)


# -----------------------------------------------------------------------------
# Now some cool charts

# Add some space
""
""
""

# DataFrameが空でない場合にのみチャートを表示
if not df.empty:
    
    st.subheader("Units left", divider="red")

    # reorder_point未満のアイテムをフィルタリング
    need_to_reorder = df[df["units_left"] < df["reorder_point"]].loc[:, "item_name"]

    if len(need_to_reorder) > 0:
        items = "\n".join(f"* {name}" for name in need_to_reorder)

        st.error(f"We're running dangerously low on the items below:\n {items}")

    ""
    ""

    st.altair_chart(
        # Layer 1: Bar chart.
        alt.Chart(df)
        .mark_bar(
            orient="horizontal",
        )
        .encode(
            x="units_left",
            y="item_name",
        )
        # Layer 2: Chart showing the reorder point.
        + alt.Chart(df)
        .mark_point(
            shape="diamond",
            filled=True,
            size=50,
            color="salmon",
            opacity=1,
        )
        .encode(
            x="reorder_point",
            y="item_name",
        ),
        use_container_width=True,
    )

    st.caption("NOTE: The :diamonds: location shows the reorder point.")

    ""
    ""
    ""

    # -----------------------------------------------------------------------------

    st.subheader("Best sellers", divider="orange")

    ""
    ""

    st.altair_chart(
        alt.Chart(df)
        .mark_bar(orient="horizontal")
        .encode(
            x="units_sold",
            y=alt.Y("item_name").sort("-x"),
        ),
        use_container_width=True,
    )
