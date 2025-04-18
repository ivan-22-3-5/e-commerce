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

    USER {
        int id PK
        string identity_provider_id
        string email 
        string password 
        string name
        bool is_admin 
        timestamp created_at
    }
    
    CATEGORY {
        int id PK
        string name
    }

    CARTITEM {
        int user_id PK
        int product_id FK
        int quantity 
    }

    ORDER {
        int id PK
        string status
        int user_id FK
        bool is_paid
        timestamp created_at
    }

    PRODUCT }o--o{ CATEGORY: ""
```