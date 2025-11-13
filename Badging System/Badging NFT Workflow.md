# Boost Badging System – NFT Integration

## Overview

This document outlines a Solana-based badging flow that mints directly to recipient wallets or stores badges in the token contract (when no wallet is provided), supports email-triggered claims, and records all badge lifecycle events. The token contract includes built-in vault functionality for storing unclaimed badges. The implementation window is estimated at three weeks.

```mermaid
sequenceDiagram
    autonumber
    participant FE as Frontend
    participant IPFS as IPFS Service
    participant DB as Database
    participant Admin as Admin Wallet
    participant Sol as Token Contract<br/>(with vault functionality)
    participant Mail as Mailing Service
    participant User as User (with email)
    participant Claim as Claim Service
    participant Wallet as User Wallet

    FE->>IPFS: Submit user + badge payload
    IPFS-->>FE: Return URI + CID metadata
    FE->>DB: Persist issuance record (user data, URI, flags)
    Admin->>FE: Initiate mint (via frontend with admin wallet)
    FE->>Admin: Request transaction signing (token IDs, URI, wallet)
    Admin->>FE: Sign mint or batch mint transaction
    FE->>Sol: Send mint transaction
    Sol-->>Wallet: Mint badge to user wallet (if provided)
    Sol-->>Sol: Store badge in contract (no wallet address)
    Sol-->>DB: Emit confirmation event (tx signatures)

    Sol-->>Mail: Trigger notification payload (wallet vs stored in contract)
    Mail-->>User: Send email (direct badge info or claim instructions)

    Note over Claim,DB: Claim service fetches record using URI<br/>and retrieves registered email address

    User->>FE: Initiate claim request (via frontend)
    FE->>Claim: Request verification code
    Claim->>DB: Generate & store one-time verification code (email, URI, timestamp, expiry)
    Claim->>Mail: Send verification code to mailing service
    Mail-->>User: Send one-time verification code
    User->>FE: Input verification code
    FE->>Claim: Submit verification code
    Claim->>DB: Retrieve stored code & validate (code, rate limits, eligibility)
    Claim->>FE: Prompt for public wallet address
    FE->>User: Display wallet address input
    User->>FE: Provide new wallet address
    FE->>Claim: Submit wallet address
    Claim->>DB: Update claim intent, log timestamp
    Claim->>Mail: Send claim request email to admin
    Mail-->>Admin: Notify admin of claim request (URI, token ID, wallet)
    Admin->>FE: Initiate transfer (via frontend with admin wallet)
    FE->>Admin: Request transaction signing (from contract to wallet)
    Admin->>FE: Sign transfer transaction
    FE->>Sol: Send transfer transaction
    Sol-->>Wallet: Deliver claimed badge to user wallet
    Sol-->>DB: Record claim completion (tx signature, wallet)
    Mail-->>User: Send claim confirmation email

    Note over DB: Maintain full lifecycle history<br/>(metadata hash, issuance, claim attempts, completion)
```

---

## End-to-End Workflow

1. **Preparation**  
   - Frontend retrieves token catalogue and recipient roster.  
   - Admin selects badge set (single or batch) and recipients.

2. **Metadata & Persistence**  
   - Frontend submits badge issuance payload to the IPFS service.  
   - IPFS returns content URI plus derived metadata (hash, gateway URL).  
   - Application persists issuance record in the database, including user data, payload hash, claim eligibility flags, and URI references.

3. **Minting**  
   - Admin initiates mint via frontend with admin wallet. Frontend requests transaction signing from admin.  
   - Admin signs mint or batch mint transaction (supplying recipient wallet if available, token IDs, and metadata URI).  
   - Frontend sends the signed transaction to the token contract.  
   - Token contract (with built-in vault functionality) validates call and mints tokens:
     - **If wallet provided**: Routes tokens directly to user wallets.
     - **If no wallet provided**: Stores tokens in the contract's internal storage (vault functionality).

4. **Notification**  
   - Post-confirmation hook (webhook or listener) enqueues email template jobs.  
   - Mailing list service delivers:  
     - **Direct wallet recipients** – badge details and blockchain links.  
     - **Contract-stored recipients** – claim instructions, emphasizing security posture.

5. **Claim (Contract-Stored Tokens Only)**  
   - User initiates claim request via frontend (using claim service link from email). Frontend requests verification code from claim service.  
   - Claim service looks up issuance by URI and extracts the registered email.  
   - Claim service generates and stores one-time verification code in database (with email, URI, timestamp, expiry) and sends it to mailing service.  
   - Mailing service sends one-time verification code to user via email and enforces rate limits.  
   - User inputs verification code through frontend. Frontend submits code to claim service.  
   - Claim service retrieves stored code from database and validates (code, rate limits, eligibility).  
   - On success, frontend prompts user for a self-custodial public wallet address.  
   - User provides wallet address through frontend. Frontend submits wallet address to claim service.  
   - Claim service updates claim intent in database and sends claim request email to Admin, including URI, token ID, and user's wallet address.  
   - Admin receives claim request notification via email.  
   - Admin initiates transfer via frontend with admin wallet. Frontend requests transaction signing from admin.  
   - Admin signs transfer transaction (from contract storage to user wallet). Frontend sends the signed transaction to token contract.  
   - System updates database with claim completion timestamp, destination wallet, and transaction signature.  
   - Confirmation email is sent to the claimant.

6. **Auditing & Reporting**  
   - Dashboard surfaces mint/claim status, IPFS hashes, and notification delivery logs.  
   - Scheduled jobs reconcile on-chain state with database records.

---
