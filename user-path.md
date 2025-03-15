```mermaid
graph TD
    Start[User Opens The App] -->|Guest| BrowseProducts[Browse Products]
    Start --> Login[Login/Register]
    Login -->|Failed| Error[Show Error & Retry]
    Login -->|Successful| UserDashboard[User Dashboard]
%% Common 
    BrowseProducts --> ViewProduct[View Product Details] -->|Probably Want to Buy?| Cart[Add to Cart]
    Cart -->|Want to Checkout?| Checkout[Checkout]
    Checkout -->|Yes, Register| FillDetails[Fill order details] --> BuyProduct[Stripe Checkout]
    Checkout -->|Already Registered| ChooseDetails[Choose Previously Saved Details] --> BuyProduct
    BuyProduct --> Confirmation[Order Confirmation]
    ViewOrders --> OrderDetails[View Order Details]
    Confirmation --> Finish[Finish]
%% Logged In 
    UserDashboard --> BrowseProducts
    UserDashboard --> ViewOrders[View/Manage Past Orders]
    UserDashboard --> ManageProfile[Manage Profile]
```