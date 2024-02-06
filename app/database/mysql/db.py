from sqlalchemy import create_engine

# 替换为您的数据库连接信息
DATABASE_URL = "mysql+pymysql://db_gamechat:qq72122219@182.254.242.30:3306/db_gamechat"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
