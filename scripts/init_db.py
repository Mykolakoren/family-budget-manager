from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.category import Category, CategoryType
from app.models.user import User, UserRole


def create_default_categories(db: Session):
    """Create default categories."""
    default_categories = [
        # Income categories
        {"name": "Salary", "type": CategoryType.INCOME, "icon": "💰", "color": "#4CAF50"},
        {"name": "Freelance", "type": CategoryType.INCOME, "icon": "💻", "color": "#2196F3"},
        {"name": "Investment", "type": CategoryType.INCOME, "icon": "📈", "color": "#FF9800"},
        {"name": "Bonus", "type": CategoryType.INCOME, "icon": "🎁", "color": "#9C27B0"},
        {"name": "Other Income", "type": CategoryType.INCOME, "icon": "💵", "color": "#607D8B"},
        
        # Expense categories
        {"name": "Food", "type": CategoryType.EXPENSE, "icon": "🍽", "color": "#F44336"},
        {"name": "Transport", "type": CategoryType.EXPENSE, "icon": "🚗", "color": "#FF5722"},
        {"name": "Entertainment", "type": CategoryType.EXPENSE, "icon": "🎬", "color": "#E91E63"},
        {"name": "Health", "type": CategoryType.EXPENSE, "icon": "⚕️", "color": "#009688"},
        {"name": "Clothes", "type": CategoryType.EXPENSE, "icon": "👔", "color": "#795548"},
        {"name": "Rent", "type": CategoryType.EXPENSE, "icon": "🏠", "color": "#3F51B5"},
        {"name": "Pets", "type": CategoryType.EXPENSE, "icon": "🐕", "color": "#CDDC39"},
        {"name": "Technology", "type": CategoryType.EXPENSE, "icon": "💻", "color": "#00BCD4"},
        {"name": "Children", "type": CategoryType.EXPENSE, "icon": "👶", "color": "#FFC107"},
        {"name": "Debts", "type": CategoryType.EXPENSE, "icon": "💳", "color": "#9E9E9E"},
        {"name": "Other Expenses", "type": CategoryType.EXPENSE, "icon": "💸", "color": "#757575"},
    ]
    
    for category_data in default_categories:
        # Check if category already exists
        existing = db.query(Category).filter(
            Category.name == category_data["name"],
            Category.is_default == True
        ).first()
        
        if not existing:
            category = Category(
                **category_data,
                is_default=True,
                is_active=True,
                user_id=None  # Default categories don't belong to specific users
            )
            db.add(category)
    
    db.commit()


def create_admin_user(db: Session):
    """Create admin user if not exists."""
    admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()
    
    if not admin_user:
        admin = User(
            email="admin@familybudget.com",
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
            is_active=True,
            preferred_language="en",
            preferred_currency="USD"
        )
        db.add(admin)
        db.commit()
        print("✅ Admin user created: admin@familybudget.com")


def init_database():
    """Initialize database with default data."""
    print("🗄️  Initializing database...")
    
    db = SessionLocal()
    try:
        # Create default categories
        print("📂 Creating default categories...")
        create_default_categories(db)
        print("✅ Default categories created")
        
        # Create admin user
        print("👤 Creating admin user...")
        create_admin_user(db)
        
        print("✅ Database initialization complete!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_database()