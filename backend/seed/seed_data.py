import os
import sys
import random
from PIL import Image, ImageDraw, ImageFont

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.session import SessionLocal, engine
from app.database.base import Base
from app.models import User, UserProfile, WardrobeItem, WardrobeItemAttribute, Outfit, OutfitItem, OutfitFeedback, UserPreference, WeatherCache
from app.config import settings

COLOR_HEX_MAP = {
    "white": "#F8F9FA",
    "black": "#212529",
    "blue": "#0D6EFD",
    "navy": "#0A192F",
    "grey": "#6C757D",
    "beige": "#D6C7B2",
    "brown": "#795548",
    "green": "#198754",
    "olive": "#556B2F",
    "red": "#DC3545",
    "burgundy": "#800020",
    "pink": "#E83E8C",
    "yellow": "#FFC107"
}

def create_sample_image(filename: str, title: str, category: str, color_name: str) -> str:
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)

    if os.path.exists(filepath):
        return f"/uploads/{filename}"

    # Generate visual graphic placeholder image with PIL
    hex_code = COLOR_HEX_MAP.get(color_name.lower(), "#495057")
    img = Image.new("RGB", (300, 300), color=hex_code)
    draw = ImageDraw.Draw(img)

    # Draw centered frame
    draw.rectangle([15, 15, 285, 285], outline="#FFFFFF" if color_name != "white" else "#333333", width=4)
    
    # Draw simple text
    text = f"{title}\n({category})"
    draw.text((30, 130), text, fill="#FFFFFF" if color_name not in ["white", "yellow", "beige"] else "#111111")

    img.save(filepath, "JPEG")
    return f"/uploads/{filename}"

ITEMS_SPEC = [
    # --- 20 SHIRTS / TOPS ---
    ("Classic White Oxford Shirt", "Shirt", "casual shirt", "white", "solid", "cotton", "regular", "casual", 4, 1, ["casual", "office", "college"], "full"),
    ("Navy Blue Slim Button-Down", "Shirt", "casual shirt", "navy", "solid", "cotton", "slim", "smart_casual", 5, 1, ["office", "date", "casual"], "full"),
    ("Light Blue Denim Shirt", "Shirt", "denim shirt", "blue", "solid", "denim", "regular", "casual", 3, 2, ["casual", "outing"], "full"),
    ("Black Graphic Streetwear Tee", "T-Shirt", "graphic tee", "black", "printed", "cotton", "oversized", "streetwear", 2, 1, ["casual", "college", "party"], "short"),
    ("Grey Heather Crewneck Tee", "T-Shirt", "basic tee", "grey", "solid", "cotton", "regular", "casual", 2, 1, ["casual", "gym", "travel"], "short"),
    ("Beige Linen Resort Shirt", "Shirt", "linen shirt", "beige", "solid", "linen", "relaxed", "casual", 3, 1, ["beach", "casual", "travel"], "short"),
    ("Olive Green Utility Polo", "Polo", "polo shirt", "olive", "solid", "cotton", "regular", "smart_casual", 4, 1, ["college", "outing", "sports"], "short"),
    ("Burgundy Heavy Cotton Hoodie", "Hoodie", "hoodie", "burgundy", "solid", "cotton", "relaxed", "streetwear", 2, 3, ["casual", "college", "travel"], "full"),
    ("Charcoal Grey Knit Sweater", "Sweater", "pullover", "grey", "knit", "wool", "regular", "smart_casual", 5, 4, ["office", "dinner", "date"], "full"),
    ("White Striped Summer Polo", "Polo", "polo shirt", "white", "striped", "cotton", "regular", "casual", 3, 1, ["casual", "outing"], "short"),
    ("Red Flannel Checked Shirt", "Shirt", "flannel shirt", "red", "plaid", "cotton", "regular", "casual", 3, 2, ["casual", "travel"], "full"),
    ("Brown Cable Knit Sweater", "Sweater", "crewneck", "brown", "knit", "wool", "regular", "casual", 4, 4, ["casual", "outing"], "full"),
    ("Pink Linen Casual Shirt", "Shirt", "casual shirt", "pink", "solid", "linen", "regular", "casual", 3, 1, ["date", "beach", "party"], "short"),
    ("Yellow Graphic Oversized Tee", "T-Shirt", "graphic tee", "yellow", "printed", "cotton", "oversized", "streetwear", 2, 1, ["party", "casual"], "short"),
    ("Navy Crewneck Basic Tee", "T-Shirt", "basic tee", "navy", "solid", "cotton", "slim", "casual", 2, 1, ["casual", "college"], "short"),
    ("Black Turtleneck Sweater", "Sweater", "turtleneck", "black", "solid", "wool", "slim", "formal", 7, 3, ["dinner", "formal event", "date"], "full"),
    ("Beige Oversized Hoodie", "Hoodie", "hoodie", "beige", "solid", "cotton", "oversized", "casual", 2, 3, ["casual", "travel"], "full"),
    ("Green Printed Hawaiian Shirt", "Shirt", "resort shirt", "green", "printed", "rayon", "relaxed", "casual", 2, 1, ["beach", "party", "travel"], "short"),
    ("White Formal Dress Shirt", "Shirt", "dress shirt", "white", "solid", "cotton", "slim", "formal", 9, 1, ["interview", "wedding", "office"], "full"),
    ("Traditional Embroidered Kurta", "Kurta", "kurta", "beige", "embroidered", "cotton", "regular", "traditional", 7, 2, ["traditional event", "wedding"], "full"),

    # --- 20 PANTS / BOTTOMS ---
    ("Dark Blue Slim Fit Jeans", "Jeans", "slim jeans", "blue", "solid", "denim", "slim", "casual", 3, 2, ["casual", "college", "outing"], None),
    ("Classic Black Denim Pants", "Jeans", "straight jeans", "black", "solid", "denim", "regular", "casual", 3, 2, ["casual", "party", "college"], None),
    ("Beige Slim Chino Trousers", "Pants", "chinos", "beige", "solid", "cotton", "slim", "smart_casual", 5, 2, ["office", "date", "casual"], None),
    ("Navy Blue Tailored Trousers", "Trousers", "dress pants", "navy", "solid", "wool", "regular", "formal", 8, 2, ["office", "interview", "wedding"], None),
    ("Charcoal Grey Dress Pants", "Trousers", "dress pants", "grey", "solid", "wool", "slim", "formal", 8, 2, ["office", "interview", "formal event"], None),
    ("Olive Cargo Utility Pants", "Pants", "cargo pants", "olive", "solid", "cotton", "relaxed", "streetwear", 2, 2, ["casual", "travel", "outing"], None),
    ("Light Blue Distressed Jeans", "Jeans", "rip jeans", "light blue", "distressed", "denim", "relaxed", "streetwear", 2, 2, ["party", "casual"], None),
    ("Khaki Casual Shorts", "Shorts", "chino shorts", "beige", "solid", "cotton", "regular", "casual", 2, 1, ["beach", "casual", "sports"], None),
    ("Black Athletic Sweatpants", "Pants", "joggers", "black", "solid", "synthetic", "relaxed", "athletic", 1, 2, ["gym", "travel", "casual"], None),
    ("Brown Corduroy Trousers", "Pants", "corduroy", "brown", "solid", "cotton", "regular", "casual", 4, 3, ["casual", "outing"], None),
    ("Grey Tailored Linen Pants", "Pants", "linen pants", "grey", "solid", "linen", "relaxed", "casual", 4, 1, ["beach", "date", "casual"], None),
    ("White Slim Chinos", "Pants", "chinos", "white", "solid", "cotton", "slim", "smart_casual", 5, 1, ["party", "date", "casual"], None),
    ("Navy Athletic Running Shorts", "Shorts", "gym shorts", "navy", "solid", "synthetic", "regular", "athletic", 1, 1, ["gym", "sports"], None),
    ("Dark Grey Stretch Jeans", "Jeans", "slim jeans", "grey", "solid", "denim", "slim", "casual", 3, 2, ["college", "casual"], None),
    ("Olive Chino Trousers", "Pants", "chinos", "olive", "solid", "cotton", "regular", "smart_casual", 5, 2, ["office", "outing"], None),
    ("Black Tailored Tuxedo Pants", "Trousers", "tuxedo pants", "black", "solid", "wool", "slim", "formal", 10, 2, ["wedding", "formal event"], None),
    ("Beige Linen Drawstring Shorts", "Shorts", "linen shorts", "beige", "solid", "linen", "relaxed", "casual", 2, 1, ["beach", "travel"], None),
    ("Burgundy Casual Chinos", "Pants", "chinos", "burgundy", "solid", "cotton", "slim", "casual", 4, 2, ["party", "date"], None),
    ("Green Army Cargo Shorts", "Shorts", "cargo shorts", "green", "solid", "cotton", "relaxed", "casual", 2, 1, ["travel", "casual"], None),
    ("Raw Indigo Denim Jeans", "Jeans", "straight jeans", "navy", "solid", "denim", "regular", "casual", 3, 2, ["casual", "college"], None),

    # --- 10 SHOES / FOOTWEAR ---
    ("Classic Minimalist White Sneakers", "Sneakers", "white sneakers", "white", "solid", "leather", "regular", "casual", 3, 1, ["casual", "college", "outing", "travel"], None),
    ("Black Leather Oxford Dress Shoes", "Shoes", "oxford shoes", "black", "solid", "leather", "regular", "formal", 9, 2, ["interview", "wedding", "office", "formal event"], None),
    ("Brown Suede Chelsea Boots", "Boots", "chelsea boots", "brown", "solid", "suede", "regular", "smart_casual", 6, 3, ["date", "dinner", "casual"], None),
    ("Navy Canvas Skate Sneakers", "Sneakers", "skate shoes", "navy", "solid", "canvas", "regular", "streetwear", 2, 1, ["casual", "college"], None),
    ("Black Athletic Running Shoes", "Sneakers", "running shoes", "black", "solid", "synthetic", "regular", "athletic", 1, 1, ["gym", "sports", "travel"], None),
    ("Tan Leather Derby Shoes", "Shoes", "derby shoes", "beige", "solid", "leather", "regular", "smart_casual", 7, 2, ["office", "dinner", "date"], None),
    ("Grey Slip-On Canvas Shoes", "Sneakers", "slip-on", "grey", "solid", "canvas", "regular", "casual", 2, 1, ["casual", "beach"], None),
    ("Brown Leather Casual Loafers", "Shoes", "loafers", "brown", "solid", "leather", "regular", "smart_casual", 6, 1, ["party", "date", "outing"], None),
    ("Black Leather Combat Boots", "Boots", "combat boots", "black", "solid", "leather", "regular", "streetwear", 4, 3, ["party", "casual"], None),
    ("Beige Leather Casual Sandals", "Sandals", "sandals", "beige", "solid", "leather", "regular", "casual", 1, 1, ["beach", "casual"], None),

    # --- 5 JACKETS / OUTERWEAR ---
    ("Classic Blue Denim Jacket", "Jacket", "denim jacket", "blue", "solid", "denim", "regular", "casual", 4, 3, ["casual", "college", "outing"], "full"),
    ("Black Leather Biker Jacket", "Jacket", "leather jacket", "black", "solid", "leather", "slim", "streetwear", 5, 3, ["party", "date", "casual"], "full"),
    ("Charcoal Wool Overcoat", "Coat", "overcoat", "grey", "solid", "wool", "regular", "formal", 9, 5, ["office", "formal event", "interview"], "full"),
    ("Beige Cotton Trench Coat", "Coat", "trench coat", "beige", "solid", "cotton", "regular", "smart_casual", 7, 4, ["office", "travel", "dinner"], "full"),
    ("Olive Green Bomber Jacket", "Jacket", "bomber jacket", "olive", "solid", "synthetic", "regular", "casual", 4, 3, ["casual", "outing", "college"], "full"),

    # --- 5 WATCHES ---
    ("Silver Minimalist Analog Watch", "Watch", "analog watch", "white", "solid", "metal", "regular", "smart_casual", 6, 1, ["office", "date", "casual"], None),
    ("Black Leather Strap Dress Watch", "Watch", "dress watch", "black", "solid", "leather", "regular", "formal", 9, 1, ["interview", "wedding", "formal event"], None),
    ("Brown Leather Vintage Watch", "Watch", "vintage watch", "brown", "solid", "leather", "regular", "casual", 5, 1, ["casual", "outing", "college"], None),
    ("Gold Classic Executive Watch", "Watch", "metal watch", "yellow", "solid", "gold", "regular", "formal", 9, 1, ["wedding", "dinner"], None),
    ("Black Digital Sport Watch", "Watch", "digital watch", "black", "solid", "rubber", "regular", "athletic", 1, 1, ["gym", "sports", "travel"], None),

    # --- 5 BELTS ---
    ("Black Genuine Leather Belt", "Belt", "dress belt", "black", "solid", "leather", "regular", "formal", 8, 1, ["office", "interview", "wedding"], None),
    ("Brown Casual Leather Belt", "Belt", "casual belt", "brown", "solid", "leather", "regular", "casual", 4, 1, ["casual", "college", "outing"], None),
    ("Navy Braided Canvas Belt", "Belt", "canvas belt", "navy", "braided", "canvas", "regular", "casual", 3, 1, ["casual", "beach"], None),
    ("Tan Leather Dress Belt", "Belt", "dress belt", "beige", "solid", "leather", "regular", "smart_casual", 6, 1, ["office", "date"], None),
    ("Dark Grey Reversible Belt", "Belt", "reversible belt", "grey", "solid", "leather", "regular", "casual", 4, 1, ["casual", "office"], None),
]

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Get or create user
        user = db.query(User).filter(User.id == 1).first()
        if not user:
            user = User(id=1, name="Alex Stylist", email="alex@example.com")
            db.add(user)
            db.flush()
            profile = UserProfile(
                user_id=1,
                age=26,
                gender_preference="all",
                height_cm=178.0,
                weight_kg=72.0,
                skin_tone="medium",
                preferred_fit="regular",
                preferred_styles=["casual", "smart_casual", "minimalist"],
                favorite_colors=["white", "blue", "navy", "grey", "black"],
                disliked_colors=["neon green"],
                location="New York"
            )
            db.add(profile)
            db.commit()

        # Remove existing items if re-seeding
        db.query(WardrobeItemAttribute).delete()
        db.query(WardrobeItem).delete()
        db.commit()

        print(f"Seeding {len(ITEMS_SPEC)} wardrobe items...")

        for idx, spec in enumerate(ITEMS_SPEC):
            title, cat, subcat, color, pattern, mat, fit, style, formality, warmth, occasions, sleeve = spec
            filename = f"seed_item_{idx+1}_{color}_{cat.lower()}.jpg"
            img_url = create_sample_image(filename, title, cat, color)

            item = WardrobeItem(
                user_id=1,
                title=title,
                category=cat,
                image_url=img_url,
                is_favorite=(idx % 5 == 0),
                is_available=True
            )
            db.add(item)
            db.flush()

            attr = WardrobeItemAttribute(
                item_id=item.id,
                subcategory=subcat,
                primary_color=color,
                color_hex=COLOR_HEX_MAP.get(color, "#495057"),
                secondary_colors=[],
                pattern=pattern,
                material=mat,
                fit=fit,
                style=style,
                formality=formality,
                seasons=["spring", "summer", "autumn", "winter"],
                warmth=warmth,
                occasions=occasions,
                sleeve_type=sleeve,
                condition="good"
            )
            db.add(attr)

        db.commit()
        print("Seeding completed successfully! 65 items created.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
