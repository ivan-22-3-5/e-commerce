```mermaid
erDiagram
    PRODUCT {
        int id PK
        string title
        string description
        float full_price
        int discount
        int quantity
        bool is_active
        timestamp created_at
        list[string] images
    }
    
    CATEGORY {
        string name PK
    }

    PRODUCT }o--o{ CATEGORY: ""
```