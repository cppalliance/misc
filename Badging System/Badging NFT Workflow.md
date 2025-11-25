# Boost Badging System – NFT-Integration Plan

## Overview

Solana-based badges are either 
- minted to user wallets (claimed) or 
- stored inside the token contract (unclaimed) until claimed.

---

## End-to-End Workflow

### Admin

1. **Preparation**  
   - Admin retrieves token catalogue and recipient roster after metric evaluation via Admin UI (Django).  
   - Admin selects badge set (single or batch) and recipients.

2. **Metadata & Persistence**  
   - Admin submits badge issuance payload to the IPFS service via Admin UI (Django). 
   - IPFS returns content URI plus derived metadata (hash, gateway URL).  
   - Application persists issuance record in the database, including user data, claim eligibility flags, and URI references.

3. **Minting / Issuance of Blockchain-backed badges**  
     - Admin initiates mint in Admin UI (Django). Browser dApp flow requests transaction signing from the admin's wallet plugin.  
     - Admin signs mint or batch mint transaction (supplying recipient wallet if available, token IDs, and metadata URI).  
     - Browser dApp flow submits the signed transaction to the token contract.  
     - Token contract (with built-in vault functionality) validates call and mints tokens:
       - If wallet provided: Routes tokens directly to user wallets.
       - If no wallet provided: Stores tokens in the contract's internal storage (vault functionality).
     - Token contract emits confirmation event with transaction signatures to the database.
     - Post-confirmation hook triggers notification payload to mailing service (indicating whether badge was sent to wallet or stored in contract).
     - Mailing service sends email to user (no clickable links; instead prompt them to log into boost.org):
       - Claimed-token recipients – badge details including mint transaction ID.
       - Unclaimed-token recipients – claim instructions, emphasizing security posture.

4. **Claim Processing (Unclaimed Tokens Only)**  
   - Admin receives webhook notification when user submits a claim request.
   - Admin initiates transfer in Admin UI (Django). Browser dApp flow requests transaction signing (from contract to wallet).
   - Admin signs transfer transaction.
   - Browser dApp flow submits the signed transfer transaction to the token contract.
   - Token contract delivers the claimed badge to the user wallet.
   - System records claim completion in the database (transaction signature, wallet, timestamp).
   - Mailing service sends claim confirmation email to the user.

5. **Auditing & Reporting**  
   - Admin accesses dashboard to view mint/claim status, IPFS hashes, and notification delivery logs.
   - Database maintains full lifecycle history (metadata hash, issuance, claim selections, completion).

---

### User


**Claiming Badges (Unclaimed Tokens Only)**  
   - User logs into the User Web App.
   - If the user has unclaimed blockchain-backed badges and no wallet address on file, the User Web App notifies them that they have unclaimed badges and guides them to create a wallet (if needed) and set a primary wallet address in their user profile.
   - Once a wallet address is set in the user profile, the User Web App displays the user's unclaimed blockchain-backed badges.
   - User selects one or more badges and submits the claim request (no per-claim wallet entry; the profile wallet is used).
   - User Web App sends the claim selection (URI, token ID) together with the user's profile `wallet_address` to the claim service.
   - Claim service updates the database with claim intent details (URI, token ID, wallet_address, timestamp).
   - Claim service sends claim request payload (URI, token ID, wallet_address) to the admin webhook.
   - User waits for admin to process the claim request.
   - User receives claim confirmation email once the badge is transferred to their wallet.

---

## Workflow Diagram

```mermaid
sequenceDiagram
    autonumber
    participant AdminUI as Admin UI (Django)
    participant UserApp as User Web App (browser)
    participant IPFS as IPFS Service
    participant DB as Database
    participant Admin as Admin Wallet
    participant Sol as Token Contract<br/>(with vault functionality)
    participant Mail as Mailing Service
    participant Hook as Admin Webhook
    participant User as User (with email)
    participant Claim as Claim Service
    participant Wallet as User Wallet

    AdminUI->>IPFS: Submit user + badge payload
    IPFS-->>AdminUI: Return URI + CID metadata
    AdminUI->>DB: Persist issuance record (user data, URI, flags)
    alt Blockchain-backed badge
        Admin->>AdminUI: Initiate mint (via Admin UI with admin wallet)
        AdminUI->>Admin: Request transaction signing (token IDs, URI, wallet)
        Admin->>AdminUI: Sign mint or batch mint transaction
        AdminUI->>Sol: Send mint transaction
        Sol-->>Wallet: Mint badge to user wallet (if provided)
        Sol-->>Sol: Store badge in contract (no wallet address)
        Sol-->>DB: Emit confirmation event (tx signatures)

        Sol-->>Mail: Trigger notification payload (wallet vs stored in contract)
        Mail-->>User: Send email (direct badge info or claim instructions)

        Note over Claim,DB: Claim service queries DB for unclaimed tokens<br/>and associated recipient metadata

        User->>UserApp: Login
        UserApp->>DB: Check for unclaimed badges and wallet on file
        DB-->>UserApp: Return unclaimed badges + wallet_on_file flag
        UserApp-->>User: If no wallet on file, prompt to add wallet address in profile
        User->>UserApp: Set or confirm profile wallet address
        UserApp->>DB: Persist `wallet_address` on user

        User->>UserApp: View claim notifications
        UserApp->>Claim: Request pending unclaimed tokens (for user with wallet on file)
        Claim->>DB: Query pending badge notifications
        Claim-->>UserApp: Return selectable notifications
        User->>UserApp: Select badges
        UserApp->>Claim: Submit claim selection (URI, token ID, wallet_from_profile)
        Claim->>DB: Update claim intent, log timestamp
        Claim->>Hook: Send claim request payload (URI, token ID, wallet_from_profile)
        Hook-->>Admin: Notify admin via webhook
        Admin->>AdminUI: Initiate transfer (via Admin UI with admin wallet)
        AdminUI->>Admin: Request transaction signing (from contract to wallet)
        Admin->>AdminUI: Sign transfer transaction
        AdminUI->>Sol: Send transfer transaction
        Sol-->>Wallet: Deliver claimed badge to user wallet
        Sol-->>DB: Record claim completion (tx signature, wallet)
        Mail-->>User: Send claim confirmation email
    else Database-only badge
        User->>UserApp: View badges in profile (no wallet required)
        UserApp->>DB: Query database-only badges
        DB-->>UserApp: Return badges
        Note over DB: Database tracks issuance, views, and acknowledgements<br/>without blockchain transactions or emails
    end

    Note over DB: Maintain full lifecycle history<br/>(metadata hash, issuance, claim selections, completion)
```

---

## Database Schema

```mermaid
erDiagram
    users {
        UUID id PK
        VARCHAR email UK
        VARCHAR wallet_address
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    badge_categories {
        UUID id PK
        VARCHAR name
        TEXT description
        TIMESTAMP created_at
    }

    badges {
        UUID id PK
        UUID category_id FK
        VARCHAR name
        TEXT description
        BYTEA image
        INTEGER badge_type
        INTEGER contract_token_id
        TEXT metadata_uri
        TIMESTAMP created_at
    }

    badge_issuances {
        UUID id PK
        UUID badge_id FK
        UUID user_id FK
        UUID issued_by FK
        TEXT metadata_uri
        INTEGER status
        VARCHAR wallet_address
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    badge_notifications {
        UUID id PK
        UUID issuance_id FK
        BOOLEAN is_read
        TIMESTAMP appeared_at
    }

    claim_intents {
        UUID id PK
        UUID issuance_id FK
        INTEGER status
        VARCHAR wallet_address
        TIMESTAMP submitted_at
        TIMESTAMP admin_response_at
    }

    badge_logs {
        UUID id PK
        INTEGER action_type
        VARCHAR entity_type
        UUID badge_id FK
        UUID category_id FK
        UUID issuance_id FK
        UUID user_id FK
        UUID claim_id FK
        UUID performed_by FK
        VARCHAR blockchain_tx_signature
        VARCHAR wallet_address
        TEXT old_value
        TEXT new_value
        INTEGER status
        TEXT error_message
        TIMESTAMP created_at
    }

    email_logs {
        UUID id PK
        UUID issuance_id FK
        INTEGER notification_type
        VARCHAR mail_provider_id
        VARCHAR status
        JSONB metadata
        TIMESTAMP created_at
    }

    %% Relationships
    badge_categories ||--o{ badges : "has"
    badges ||--o{ badge_issuances : "issued_as"
    users ||--o{ badge_issuances : "receives"
    users ||--o{ badge_issuances : "issues"
    badge_issuances ||--o{ badge_notifications : "triggers"
    badge_issuances ||--o{ claim_intents : "claimed_via"
    badge_issuances ||--o{ email_logs : "notified_via"
    users ||--o{ badge_logs : "performed_by"
    badges ||--o{ badge_logs : "logged"
    badge_categories ||--o{ badge_logs : "logged"
    badge_issuances ||--o{ badge_logs : "logged"
    users ||--o{ badge_logs : "logged"
    claim_intents ||--o{ badge_logs : "logged"
```

**Note on `wallet_address` in `users` table**: The `wallet_address` field in the `users` table is used both to support batch minting operations by admins and to drive the user-initiated claim flow. When an admin executes a batch-mint action, it would be impossible to manually input all wallet addresses for each recipient. Therefore, users who have a wallet address should set it in their profile page. If a user has not set their wallet address, their badge tokens are automatically minted to the token contract (vault functionality) instead of directly to their wallet, requiring them to claim the badge later. When a user later claims an unclaimed badge, the system uses the `wallet_address` stored on the user profile (rather than letting the user enter multiple arbitrary wallets per claim).
