from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.wardrobe import WardrobeItem, WardrobeItemAttribute
from app.schemas.wardrobe import WardrobeItemCreate, WardrobeItemUpdate

class WardrobeService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_items(
        self,
        user_id: int,
        category: Optional[str] = None,
        search: Optional[str] = None,
        is_favorite: Optional[bool] = None,
        is_available: Optional[bool] = None
    ) -> List[WardrobeItem]:
        query = self.db.query(WardrobeItem).filter(WardrobeItem.user_id == user_id)
        
        if category and category != "All":
            query = query.filter(WardrobeItem.category == category)
        if is_favorite is not None:
            query = query.filter(WardrobeItem.is_favorite == is_favorite)
        if is_available is not None:
            query = query.filter(WardrobeItem.is_available == is_available)
        if search:
            search_term = f"%{search}%"
            query = query.filter(WardrobeItem.title.ilike(search_term))

        return query.order_by(WardrobeItem.created_at.desc()).all()

    def get_item_by_id(self, item_id: int) -> Optional[WardrobeItem]:
        return self.db.query(WardrobeItem).filter(WardrobeItem.id == item_id).first()

    def create_item(self, user_id: int, data: WardrobeItemCreate) -> WardrobeItem:
        item = WardrobeItem(
            user_id=user_id,
            title=data.title,
            category=data.category,
            image_url=data.image_url,
            is_favorite=data.is_favorite or False,
            is_available=data.is_available if data.is_available is not None else True
        )
        self.db.add(item)
        self.db.flush()

        attr_data = data.attributes
        if attr_data:
            attributes = WardrobeItemAttribute(
                item_id=item.id,
                subcategory=attr_data.subcategory,
                primary_color=attr_data.primary_color or "white",
                secondary_colors=attr_data.secondary_colors or [],
                color_hex=attr_data.color_hex or "#FFFFFF",
                pattern=attr_data.pattern or "solid",
                material=attr_data.material or "cotton",
                fit=attr_data.fit or "regular",
                style=attr_data.style or "casual",
                formality=attr_data.formality or 3,
                seasons=attr_data.seasons or ["spring", "summer"],
                warmth=attr_data.warmth or 1,
                occasions=attr_data.occasions or ["casual"],
                sleeve_type=attr_data.sleeve_type,
                condition=attr_data.condition or "good"
            )
            self.db.add(attributes)
        else:
            default_attr = WardrobeItemAttribute(
                item_id=item.id,
                primary_color="white",
                color_hex="#FFFFFF",
                formality=3,
                warmth=1,
                occasions=["casual"]
            )
            self.db.add(default_attr)

        self.db.commit()
        self.db.refresh(item)
        return item

    def create_batch_items(self, user_id: int, items_data: List[WardrobeItemCreate]) -> List[WardrobeItem]:
        created_items = []
        for data in items_data:
            item = self.create_item(user_id, data)
            created_items.append(item)
        return created_items

    def update_item(self, item_id: int, data: WardrobeItemUpdate) -> Optional[WardrobeItem]:
        item = self.get_item_by_id(item_id)
        if not item:
            return None

        if data.title is not None:
            item.title = data.title
        if data.category is not None:
            item.category = data.category
        if data.image_url is not None:
            item.image_url = data.image_url
        if data.is_favorite is not None:
            item.is_favorite = data.is_favorite
        if data.is_available is not None:
            item.is_available = data.is_available

        if data.attributes and item.attributes:
            attr = item.attributes
            attr_data = data.attributes
            for field, val in attr_data.model_dump(exclude_unset=True).items():
                setattr(attr, field, val)

        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_item(self, item_id: int) -> bool:
        item = self.get_item_by_id(item_id)
        if not item:
            return False
        self.db.delete(item)
        self.db.commit()
        return True
