# BookSwap Use Cases Documentation

## System Overview
BookSwap is a peer-to-peer book exchange platform with AI-powered recommendations, real-time chat, and social features.

## Actors

### Primary Actor: User (Reader)
- **Description**: A book enthusiast who wants to exchange books, get recommendations, and connect with other readers
- **Goals**: Find books, exchange books, discover new reads, connect with community

## Use Cases

### UC-01: User Registration
**Actor**: User  
**Description**: New user creates an account to access the platform

**Preconditions**:
- User has valid email address
- User chooses unique username

**Main Flow**:
1. User navigates to registration page
2. User enters personal information (email, username, password, full name, bio, city)
3. System validates input data
4. System creates user account
5. System generates JWT tokens
6. User is automatically logged in
7. System sends welcome event

**Alternative Flows**:
- **4a**: Email already exists
  - System displays error message
  - User must use different email
- **4b**: Username already taken
  - System displays error message
  - User must choose different username
- **4c**: Invalid input data
  - System displays validation errors
  - User corrects input and resubmits

**Postconditions**:
- User account created
- User logged in
- User can access all platform features

---

### UC-02: User Login
**Actor**: User  
**Description**: Registered user authenticates to access their account

**Preconditions**:
- User has valid account
- User knows credentials

**Main Flow**:
1. User navigates to login page
2. User enters email and password
3. System validates credentials
4. System generates JWT tokens
5. User is redirected to dashboard
6. System records login event

**Alternative Flows**:
- **3a**: Invalid credentials
  - System displays error message
  - User must retry or reset password
- **3b**: Account disabled
  - System displays account disabled message
  - User must contact support

**Postconditions**:
- User authenticated
- User can access personalized features

---

### UC-03: Search Books
**Actor**: User  
**Description**: User searches for books to find interesting reads

**Preconditions**:
- User is logged in

**Main Flow**:
1. User navigates to books section
2. User enters search query (title, author, genre)
3. System performs database search
4. System displays matching books
5. User can filter results by genre, condition, location

**Alternative Flows**:
- **4a**: No books found
  - System displays "no results" message
  - User can modify search criteria

**Postconditions**:
- User sees relevant book listings
- User can proceed to exchange or wishlist

---

### UC-04: Create Book Listing
**Actor**: User  
**Description**: User adds their book to the platform for exchange

**Preconditions**:
- User is logged in
- User owns the physical book

**Main Flow**:
1. User navigates to "Add Book" page
2. User enters book details (title, author, ISBN, genre, condition, description)
3. System validates book information
4. System creates book record
5. Book is marked as owned by user
6. System sends book creation event
7. User can now offer book for exchange

**Alternative Flows**:
- **4a**: Invalid ISBN or duplicate listing
  - System displays validation error
  - User corrects information

**Postconditions**:
- Book listed in platform
- Book available for exchanges
- User marked as book owner

---

### UC-05: Request Book Exchange
**Actor**: User  
**Description**: User initiates exchange of their book for another user's book

**Preconditions**:
- User is logged in
- User has books available for exchange
- Target book is available for exchange

**Main Flow**:
1. User views target book details
2. User clicks "Exchange" button
3. User selects their book to offer
4. User adds optional message
5. System validates exchange request
6. System creates exchange record
7. System sends exchange creation event
8. Target user receives notification

**Alternative Flows**:
- **6a**: User tries to exchange with themselves
  - System displays error message
- **6b**: User's book not available
  - System displays error message
- **6c**: Target book not available
  - System displays error message

**Postconditions**:
- Exchange request created
- Exchange status set to "pending"
- Target user notified

---

### UC-06: Manage Exchange Requests
**Actor**: User  
**Description**: User handles incoming exchange requests

**Preconditions**:
- User has pending exchange requests

**Main Flow**:
1. User navigates to "My Exchanges"
2. User views pending requests
3. User selects specific request
4. User reviews exchange details
5. User chooses action (accept/reject)
6. System updates exchange status
7. System sends status update event
8. Other user receives notification

**Alternative Flows**:
- **5a**: Exchange already processed
  - System displays status message

**Postconditions**:
- Exchange status updated
- Both users notified
- If accepted: books marked for exchange

---

### UC-07: Complete Book Exchange
**Actor**: User  
**Description**: Users complete the physical exchange of books

**Preconditions**:
- Exchange is accepted
- Both users agree to complete exchange

**Main Flow**:
1. User navigates to accepted exchange
2. User clicks "Complete Exchange"
3. System confirms exchange completion
4. System updates exchange status to "completed"
5. System sends completion event
6. Books marked as exchanged
7. Both users can leave reviews

**Postconditions**:
- Exchange completed
- Books ownership updated
- Users can rate experience

---

### UC-08: Real-time Chat
**Actor**: User  
**Description**: Users communicate during exchange process

**Preconditions**:
- Exchange exists between users
- Exchange status is not "completed"

**Main Flow**:
1. User opens chat with exchange partner
2. User types message
3. System validates message content
4. System sends message via WebSocket
5. Message appears in real-time for both users
6. System stores message in database
7. System sends message event

**Alternative Flows**:
- **4a**: Message content invalid
  - System displays validation error
- **4b**: User not exchange participant
  - System denies access

**Postconditions**:
- Message delivered
- Chat history preserved
- Users can continue conversation

---

### UC-09: Add Friends
**Actor**: User  
**Description**: User builds social network with other readers

**Preconditions**:
- User is logged in
- Target user exists

**Main Flow**:
1. User searches for other users
2. User finds target user profile
3. User clicks "Add Friend"
4. System creates friendship record
5. System sends friend addition event
6. Users appear in each other's friends list

**Alternative Flows**:
- **4a**: Trying to add self as friend
  - System displays error message
- **4b**: Already friends
  - System displays status message

**Postconditions**:
- Friendship established
- Users can see each other's activity
- Enhanced social features available

---

### UC-10: Manage Wishlist
**Actor**: User  
**Description**: User tracks books they want to read or acquire

**Preconditions**:
- User is logged in

**Main Flow**:
1. User views book details
2. User clicks "Add to Wishlist"
3. System adds book to user's wishlist
4. User can manage wishlist items
5. User receives notifications when wishlist books become available

**Alternative Flows**:
- **3a**: Book already in wishlist
  - System displays status message

**Postconditions**:
- Book added to wishlist
- User can track desired books
- Notification system enabled

---

### UC-11: Write Book Review
**Actor**: User  
**Description**: User shares their opinion about books they've read

**Preconditions**:
- User has read or exchanged the book
- User is logged in

**Main Flow**:
1. User navigates to book page
2. User clicks "Write Review"
3. User rates book (1-5 stars)
4. User writes review content
5. System validates review data
6. System creates review record
7. System sends review creation event
8. Review appears on book page

**Alternative Flows**:
- **5a**: User already reviewed this book
  - System offers to update existing review
- **5b**: Invalid review content
  - System displays validation errors

**Postconditions**:
- Review published
- Book rating updated
- Community benefits from review

---

### UC-12: Get AI Recommendations
**Actor**: User  
**Description**: User receives personalized book suggestions

**Preconditions**:
- User is logged in
- User has reading history or preferences

**Main Flow**:
1. User navigates to recommendations page
2. System analyzes user's reading history
3. System considers user's favorite genres
4. AI generates personalized recommendations
5. System displays recommended books
6. User can save recommendations to wishlist

**Alternative Flows**:
- **2a**: No reading history available
  - System provides general recommendations
- **4a**: AI service unavailable
  - System falls back to genre-based recommendations

**Postconditions**:
- User receives personalized suggestions
- Discovery of new books
- Enhanced user engagement

---

### UC-13: View User Profile
**Actor**: User  
**Description**: User views another user's profile and activity

**Preconditions**:
- User is logged in
- Target user exists

**Main Flow**:
1. User clicks on another user's name
2. System displays user profile modal
3. User sees profile information
4. User views user's books and reviews
5. User can initiate chat or exchange

**Alternative Flows**:
- **2a**: User profile not found
  - System displays error message

**Postconditions**:
- User learns about other community member
- Social interaction opportunities identified

---

## System Events

### Event Types
- **USER_REGISTERED** - New user account created
- **BOOK_CREATED** - New book listed
- **EXCHANGE_CREATED** - Exchange request initiated
- **EXCHANGE_ACCEPTED** - Exchange approved
- **EXCHANGE_COMPLETED** - Exchange finished
- **MESSAGE_SENT** - Chat message delivered
- **FRIEND_ADDED** - Friendship established
- **REVIEW_CREATED** - New review published

### Event Handling
- **Logging Observer** - Records all system events
- **Statistics Observer** - Tracks usage metrics
- **WebSocket Observer** - Real-time notifications
- **Email Observer** - Email notifications for important events

## Non-Functional Requirements

### Performance
- Response time < 2 seconds for API calls
- Real-time message delivery < 500ms
- Support 100+ concurrent users

### Security
- JWT token authentication
- Input validation and sanitization
- CORS protection
- SQL injection prevention

### Usability
- Intuitive user interface
- Mobile-responsive design
- Clear error messages
- Progressive disclosure of features

### Reliability
- 99.9% uptime target
- Graceful error handling
- Data backup and recovery
- Comprehensive logging

## Conclusion

These use cases cover the complete user journey through the BookSwap platform, from registration to active participation in the book exchange community. The system is designed to be user-friendly while maintaining robust security and performance standards.
