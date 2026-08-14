"""Categories, kinds, and hierarchical item taxonomy with item_type as single source of truth."""

KINDS = ["clothing", "footwear", "accessory"]

CATEGORY_GROUPS = {
    "upper_body": [
        "blazer", "suit jacket", "sports jacket", "jacket", "coat",
        "dress shirt", "shirt", "casual shirt", "t-shirt", "polo shirt", "hoodie",
        "sweater", "cardigan", "waistcoat", "vest", "kurta"
    ],
    "lower_body": [
        "suit trousers", "formal trousers", "trousers", "pants",
        "jeans", "chinos", "cargo pants", "loose pants", "wide leg pants",
        "shorts", "joggers", "pajama", "skirt"
    ],
    "footwear": [
        "formal shoes", "formal leather shoes", "oxford shoes", "derby shoes", "loafers",
        "monk strap shoes", "dress boots", "chelsea boots", "sneakers",
        "running shoes", "sports shoes", "sandals", "slides", "slippers", "flip flops", "boots"
    ],
    "accessory": [
        "tie", "bow tie", "watch", "belt", "bag", "cap", "hat", "glasses", "sunglasses"
    ]
}

ITEM_TAXONOMY = {
    "suit_jacket": {
        "kind": "clothing",
        "group": "upper_body",
        "category": "suit jacket",
        "display_name": "Suit Jacket",
        "default_style": "formal",
        "formality_range": [9, 10]
    },
    "blazer": {
        "kind": "clothing",
        "group": "upper_body",
        "category": "blazer",
        "display_name": "Blazer",
        "default_style": "smart casual",
        "formality_range": [6, 8]
    },
    "dress_shirt": {
        "kind": "clothing",
        "group": "upper_body",
        "category": "dress shirt",
        "display_name": "Dress Shirt",
        "default_style": "formal",
        "formality_range": [7, 9]
    },
    "casual_shirt": {
        "kind": "clothing",
        "group": "upper_body",
        "category": "casual shirt",
        "display_name": "Casual Shirt",
        "default_style": "casual",
        "formality_range": [2, 4]
    },
    "t_shirt": {
        "kind": "clothing",
        "group": "upper_body",
        "category": "t-shirt",
        "display_name": "T-Shirt",
        "default_style": "casual",
        "formality_range": [1, 3]
    },
    "hoodie": {
        "kind": "clothing",
        "group": "upper_body",
        "category": "hoodie",
        "display_name": "Hoodie",
        "default_style": "casual",
        "formality_range": [1, 3]
    },
    "suit_trousers": {
        "kind": "clothing",
        "group": "lower_body",
        "category": "suit trousers",
        "display_name": "Suit Trousers",
        "default_style": "formal",
        "formality_range": [8, 9]
    },
    "formal_trousers": {
        "kind": "clothing",
        "group": "lower_body",
        "category": "formal trousers",
        "display_name": "Formal Trousers",
        "default_style": "formal",
        "formality_range": [7, 8]
    },
    "loose_pants": {
        "kind": "clothing",
        "group": "lower_body",
        "category": "loose pants",
        "display_name": "Loose Pants",
        "default_style": "casual",
        "formality_range": [2, 4]
    },
    "jeans": {
        "kind": "clothing",
        "group": "lower_body",
        "category": "jeans",
        "display_name": "Jeans",
        "default_style": "casual",
        "formality_range": [2, 4]
    },
    "chinos": {
        "kind": "clothing",
        "group": "lower_body",
        "category": "chinos",
        "display_name": "Chinos",
        "default_style": "smart casual",
        "formality_range": [4, 6]
    },
    "joggers": {
        "kind": "clothing",
        "group": "lower_body",
        "category": "joggers",
        "display_name": "Joggers",
        "default_style": "sporty",
        "formality_range": [1, 3]
    },
    "shorts": {
        "kind": "clothing",
        "group": "lower_body",
        "category": "shorts",
        "display_name": "Shorts",
        "default_style": "casual",
        "formality_range": [1, 3]
    },
    "formal_leather_shoes": {
        "kind": "footwear",
        "group": "footwear",
        "category": "formal shoes",
        "display_name": "Formal Leather Shoes",
        "default_style": "formal",
        "formality_range": [8, 9]
    },
    "oxford_shoes": {
        "kind": "footwear",
        "group": "footwear",
        "category": "oxford shoes",
        "display_name": "Oxford Shoes",
        "default_style": "formal",
        "formality_range": [8, 10]
    },
    "loafers": {
        "kind": "footwear",
        "group": "footwear",
        "category": "loafers",
        "display_name": "Loafers",
        "default_style": "smart casual",
        "formality_range": [6, 8]
    },
    "sneakers": {
        "kind": "footwear",
        "group": "footwear",
        "category": "sneakers",
        "display_name": "Sneakers",
        "default_style": "casual",
        "formality_range": [1, 3]
    },
    "sandals": {
        "kind": "footwear",
        "group": "footwear",
        "category": "sandals",
        "display_name": "Sandals",
        "default_style": "casual",
        "formality_range": [1, 3]
    },
    "slides": {
        "kind": "footwear",
        "group": "footwear",
        "category": "slides",
        "display_name": "Slides",
        "default_style": "casual",
        "formality_range": [1, 2]
    }
}

CATEGORIES = [
    "shirt", "t-shirt", "polo shirt", "dress shirt", "blazer", "suit jacket",
    "sports jacket", "jacket", "coat", "hoodie", "sweater", "cardigan",
    "waistcoat", "vest", "jeans", "trousers", "formal trousers", "suit trousers",
    "chinos", "cargo pants", "shorts", "joggers", "sneakers", "formal shoes",
    "oxford shoes", "derby shoes", "loafers", "boots", "sandals", "slippers",
    "watch", "belt", "tie", "bow tie", "bag", "cap", "hat", "glasses",
    "sunglasses", "other"
]

FOOTWEAR_TAXONOMY = [
    "formal shoes", "formal leather shoes", "oxford shoes", "derby shoes", "loafers",
    "monk strap shoes", "dress boots", "chelsea boots", "sneakers",
    "running shoes", "sports shoes", "sandals", "slippers", "flip flops"
]

SUBCATEGORIES = {
    "jacket": ["Suit Jacket / Blazer", "Suit Jacket", "Blazer", "Denim Jacket", "Leather Jacket", "Bomber Jacket", "Puffer Jacket"],
    "blazer": ["Suit Jacket", "Blazer", "Single-Breasted Blazer", "Double-Breasted Blazer"],
    "suit jacket": ["Suit Jacket", "Blazer", "Tuxedo Jacket"],
    "shirt": ["Dress Shirt", "Resort Shirt / Printed Shirt", "Button-Down Shirt", "Flannel Shirt"],
    "dress shirt": ["Formal Dress Shirt", "Button-Down Dress Shirt", "Tuxedo Shirt"],
    "t-shirt": ["Crewneck T-Shirt", "V-Neck T-Shirt", "Graphic T-Shirt", "Oversized T-Shirt"],
    "pants": ["Suit Trousers", "Formal Trousers", "Chinos", "Cargo Pants", "Linen Pants / Casual Trousers", "Track Pants"],
    "trousers": ["Suit Trousers", "Formal Trousers", "Pleated Trousers", "Chinos"],
    "suit trousers": ["Suit Trousers", "Formal Suit Trousers", "Dress Pants"],
    "jeans": ["Slim Jeans", "Straight Jeans", "Skinny Jeans", "Baggy Jeans"],
    "shoes": ["Dress Shoes / Loafers", "Oxford Shoes", "Derby Shoes", "Monk Strap Shoes"],
    "formal shoes": ["Oxford Shoes", "Derby Shoes", "Loafers", "Monk Strap Shoes"],
    "sneakers": ["Athletic Sneakers", "Low-Top Canvas Sneakers", "High-Top Sneakers", "Running Shoes"],
    "sandals": ["Slides / Slippers", "Flip-Flops", "Leather Sandals"]
}
