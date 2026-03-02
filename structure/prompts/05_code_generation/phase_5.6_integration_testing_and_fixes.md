# Phase 5.6: Integration Testing & Deployment Validation

---

## Orchestration Information

**Phase**: Phase 5 - Code Generation
**Step**: Step 5.6 - Integration Testing & Deployment Validation
**Team Supervisor**: development_team_supervisor
**Assigned Agent**: development_specialist_test_generation
**Task File Name**: {{TASKS_BASE_PATH}}/phase_5.6_integration_validation.md

### Expected Deliverables

1. **Database Seed Data Script**
   - Location: `{{CODE_GENERATION_BACKEND_OUTPUT}}/src/main/resources/data/seed-data.sql`
   - Description: SQL script to create test users and sample data
   - Includes: Test users with correct password hashes, sample transactions, reference data

2. **Integration Test Report**
   - Location: `{{CODE_GENERATION_BASE_PATH}}/INTEGRATION-TEST-REPORT.md`
   - Description: Results of integration testing for all workpackages
   - Includes: Test results, issues found, fixes applied

3. **Deployment Guide**
   - Location: `{{CODE_GENERATION_BASE_PATH}}/DEPLOYMENT.md`
   - Description: Step-by-step deployment instructions
   - Includes: Prerequisites, startup commands, test credentials, troubleshooting

4. **Issue Fixes**
   - Location: Various files in `{{CODE_GENERATION_BACKEND_OUTPUT}}/`
   - Description: Code fixes for integration issues discovered during testing
   - Includes: Enum converters, security config, SQL fixes, validation adjustments

### Success Criteria
- [ ] Database seed data created and tested
- [ ] All workpackages tested end-to-end with real database
- [ ] Login works with test users
- [ ] All CRUD operations work
- [ ] Frontend can call backend APIs
- [ ] Integration issues documented and fixed
- [ ] Deployment guide complete with test credentials

---

## Context

### Input Locations
- **Generated Backend Code**: `{{CODE_GENERATION_BACKEND_OUTPUT}}/`
- **Generated Frontend Code**: `{{CODE_GENERATION_FRONTEND_OUTPUT}}/`
- **Database Schema**: `{{CODE_GENERATION_BACKEND_OUTPUT}}/src/main/resources/db/migration/`
- **Technical Specs**: `{{TECH_SPEC_BASE_PATH}}/`
- **Business Specs**: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/`
- **Test Specs**: `{{TEST_CASE_GENERATION_BASE_PATH}}/`

### Output Locations
- **Seed Data**: `{{CODE_GENERATION_BACKEND_OUTPUT}}/src/main/resources/data/seed-data.sql`
- **Test Report**: `{{CODE_GENERATION_BASE_PATH}}/INTEGRATION-TEST-REPORT.md`
- **Deployment Guide**: `{{CODE_GENERATION_BASE_PATH}}/DEPLOYMENT.md`
- **Fixed Code**: Various locations in backend/frontend

---

## Objective

Validate that all generated code works together as an integrated system. Test with real database, real HTTP requests, and real user flows. Fix any integration issues discovered. Create deployment documentation and seed data for testing.

**This phase bridges the gap between unit tests (which pass) and production deployment (which may fail due to integration issues).**

---

## Instructions

### 1. Analyze Generated Code

1. **Review all workpackages implemented**:
   - Check `{{CODE_GENERATION_STATUS}}`
   - List all workpackages with status "completed"
   - Note which have backend, frontend, and tests

2. **Identify potential integration issues**:
   - **Enum mappings**: Check if entities use `@Enumerated(EnumType.STRING)` with code-based enums
   - **SQL keywords**: Check for table names like `transaction`, `user`, `order`, `group`
   - **Security config**: Check if CSRF is disabled for REST APIs
   - **Password handling**: Check if passwords are case-normalized before hashing
   - **Validation rules**: Check if `@Size` constraints match actual data needs

3. **Review database schema**:
   - Check `{{CODE_GENERATION_BACKEND_OUTPUT}}/src/main/resources/db/migration/`
   - Note table names, column types, enum values
   - Identify reserved keywords

### 2. Create Database Seed Data

**Create file**: `{{CODE_GENERATION_BACKEND_OUTPUT}}/src/main/resources/data/seed-data.sql`

**Include**:

1. **Test Users** (for WP-001 or authentication workpackage):
   ```sql
   -- Admin user: ADMIN001 / password
   INSERT INTO user_table (user_id, first_name, last_name, password_hash, user_type, created_at, updated_at)
   VALUES ('ADMIN001', 'Admin', 'User', '$2a$10$...', 'A', datetime('now'), datetime('now'));
   
   -- Regular user: USER001 / password
   INSERT INTO user_table (user_id, first_name, last_name, password_hash, user_type, created_at, updated_at)
   VALUES ('USER001', 'Test', 'User', '$2a$10$...', 'U', datetime('now'), datetime('now'));
   ```
   
   **CRITICAL - Password Hashing**:
   - Check authentication service to see if passwords are uppercased before hashing
   - If yes, hash "PASSWORD" not "password"
   - Use BCrypt with strength 10: `htpasswd -bnBC 10 '' PASSWORD`
   - Document the password in comments

2. **Sample Data** (for each entity):
   - Create 2-3 sample records per entity
   - Use enum values that match entity definitions
   - Ensure foreign keys reference existing records
   - Use realistic test data

3. **Reference Data** (if applicable):
   - Lookup tables
   - Configuration data
   - Static reference data

**Example**:
```sql
-- ============================================
-- Seed Data for CardDemo Application
-- ============================================
-- Purpose: Test data for development and integration testing
-- Password for all users: "password" (hashed as "PASSWORD" if uppercased)
-- ============================================

-- Test Users (WP-001)
INSERT INTO aws_m2_carddemo_usrsec_vsam_ksds (sec_usr_id, sec_usr_fname, sec_usr_lname, sec_usr_pwd, sec_usr_type, created_at, updated_at)
VALUES 
('ADMIN001', 'Admin', 'User', '$2y$10$irACuuejTyaROdgcm80SWu21OjxI8BHNaR.7gXZ8rO/8PXJ6bnsa.', 'A', datetime('now'), datetime('now')),
('USER001', 'Test', 'User', '$2y$10$irACuuejTyaROdgcm80SWu21OjxI8BHNaR.7gXZ8rO/8PXJ6bnsa.', 'U', datetime('now'), datetime('now'));

-- Sample Transactions (WP-003)
INSERT INTO "transaction" (transaction_id, card_number, type_code, category_code, source, amount, description, original_timestamp, processing_timestamp, merchant_id, merchant_name, merchant_city, merchant_zip, created_at, updated_at)
VALUES 
('TX0000000001', '4111111111111111', 'PU', 'FOOD', 'POS', 125.50, 'Coffee Shop', datetime('now', '-2 days'), datetime('now', '-2 days'), 'M00001', 'Starbucks', 'New York', '10001', datetime('now'), datetime('now')),
('TX0000000002', '4111111111111111', 'PU', 'FOOD', 'POS', 89.99, 'Grocery Store', datetime('now', '-1 day'), datetime('now', '-1 day'), 'M00002', 'Whole Foods', 'Boston', '02101', datetime('now'), datetime('now'));
```

### 3. Test Database Integration

1. **Start application with seed data**:
   ```bash
   cd {{CODE_GENERATION_BACKEND_OUTPUT}}
   mvn spring-boot:run
   ```

2. **Check for startup errors**:
   - SQL syntax errors (reserved keywords?)
   - Enum mapping errors (code vs name mismatch?)
   - Schema validation errors (constraint violations?)
   - Bean creation errors (missing converters?)

3. **If errors found, fix them**:
   - **SQL reserved keywords**: Quote table names `@Table(name = "\"transaction\"")`
   - **Enum mapping**: Create `@Converter` classes for code-based enums
   - **Security**: Add SecurityFilterChain to disable CSRF for REST APIs
   - **Validation**: Adjust `@Size` constraints to match actual data

### 4. Test API Endpoints

For each workpackage, test the main API endpoints with curl:

**Example - Test Login (WP-001)**:
```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"userId":"ADMIN001","password":"password"}'
```

**Expected**: JSON response with user info and redirect URL

**Example - Test Create User (WP-002)**:
```bash
curl -X POST http://localhost:8080/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"userId":"TEST001","firstName":"Test","lastName":"User","password":"test1234","userType":"U"}'
```

**Expected**: JSON response with created user

**Example - Test Get Transaction (WP-003)**:
```bash
curl http://localhost:8080/api/v1/transactions/TX0000000001
```

**Expected**: JSON response with transaction details

**Document all test results** in integration test report.

### 5. Test Frontend Integration

1. **Start frontend**:
   ```bash
   cd {{CODE_GENERATION_FRONTEND_OUTPUT}}
   npm run dev
   ```

2. **Test each workpackage flow**:
  

3. **Check browser console for errors**:
   - CORS errors? (Add frontend origin to CORS config)
   - 403 Forbidden? (CSRF not disabled)
   - 401 Unauthorized? (Password hash mismatch)
   - Network errors? (Backend not running)

### 6. Fix Integration Issues

**Common Issues and Fixes**:

#### Issue 1: Enum Mapping Error
**Symptom**: `No enum constant com.example.UserType.A`
**Cause**: Database has code 'A', enum expects name 'ADMIN'
**Fix**: Create JPA converter
```java
@Converter(autoApply = true)
public class UserTypeConverter implements AttributeConverter<UserType, String> {
    @Override
    public String convertToDatabaseColumn(UserType userType) {
        return userType == null ? null : String.valueOf(userType.getCode());
    }
    
    @Override
    public UserType convertToEntityAttribute(String code) {
        return code == null ? null : UserType.fromCode(code.charAt(0));
    }
}
```
Update entity: `@Convert(converter = UserTypeConverter.class)`

#### Issue 2: SQL Reserved Keyword
**Symptom**: `SQL error near "transaction"`
**Cause**: `transaction` is reserved keyword in SQLite
**Fix**: Quote table name in entity and migration
```java
@Table(name = "\"transaction\"")
```

#### Issue 3: CSRF Protection Blocking API
**Symptom**: 403 Forbidden on POST requests
**Cause**: Spring Security CSRF enabled by default
**Fix**: Add SecurityFilterChain
```java
@Bean
public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
    http
        .csrf(csrf -> csrf.disable())
        .cors(cors -> cors.configurationSource(corsConfigurationSource()))
        .authorizeHttpRequests(auth -> auth.anyRequest().permitAll());
    return http.build();
}
```

#### Issue 4: Password Hash Mismatch
**Symptom**: Login fails with correct password
**Cause**: Password uppercased before hashing but seed data uses lowercase
**Fix**: Update seed data with correct hash
```bash
htpasswd -bnBC 10 '' PASSWORD  # If uppercased
htpasswd -bnBC 10 '' password  # If not uppercased
```

#### Issue 5: Validation Too Strict
**Symptom**: Validation error "must be 16 characters" but data is 12
**Cause**: `@Size(min=16, max=16)` doesn't match actual data
**Fix**: Adjust validation
```java
@Size(min=1, max=16, message="Must be 1-16 characters")
```

### 7. Create Integration Test Report

**Create file**: `{{CODE_GENERATION_BASE_PATH}}/INTEGRATION-TEST-REPORT.md`

**Template**:
```markdown
# Integration Test Report

## Test Date
[Date and time]

## Workpackages Tested
- WP-001: [Name] - ✅ PASS / ❌ FAIL
- WP-002: [Name] - ✅ PASS / ❌ FAIL
- WP-003: [Name] - ✅ PASS / ❌ FAIL

## Test Environment
- Database: [SQLite/PostgreSQL/etc.]
- Backend: Spring Boot [version]
- Frontend: React + Vite
- Java: [version]
- Node: [version]

## Test Results

### WP-001: [Workpackage Name]
**Status**: ✅ PASS

**Tests Performed**:
1. Login with admin user - ✅ PASS
2. Login with regular user - ✅ PASS
3. Login with invalid credentials - ✅ PASS (correct error)
4. Frontend redirect after login - ✅ PASS

**Issues Found**: None

---

### WP-002: [Workpackage Name]
**Status**: ❌ FAIL → ✅ FIXED

**Tests Performed**:
1. Create user via API - ❌ FAIL (enum mapping error)
2. Create user via frontend - ❌ FAIL (CORS error)

**Issues Found**:
1. **Enum Mapping Error**
   - Error: `No enum constant UserType.A`
   - Cause: Database stores 'A', enum expects 'ADMIN'
   - Fix: Created UserTypeConverter
   - Status: ✅ FIXED

2. **CORS Error**
   - Error: CORS policy blocked request
   - Cause: Frontend origin not in CORS config
   - Fix: Added localhost:3000 to CORS allowed origins
   - Status: ✅ FIXED

**Retest Results**: ✅ ALL PASS

---

## Summary

**Total Workpackages**: 5
**Passed**: 5
**Failed**: 0
**Issues Found**: 8
**Issues Fixed**: 8

## Common Issues Fixed

1. Enum converters created for UserType, TransactionTypeCode, TransactionCategoryCode
2. SQL reserved keyword "transaction" quoted in entity and migration
3. CSRF disabled for REST APIs
4. CORS configured for frontend origins
5. Password hashing corrected (uppercase before hash)
6. Validation rules adjusted to match actual data
7. Seed data created with correct enum values
8. Test users created with proper password hashes

## Deployment Readiness

✅ All integration tests passing
✅ Seed data created and tested
✅ Deployment guide created
✅ Test credentials documented
✅ Known issues resolved

**Status**: READY FOR DEPLOYMENT
```

### 8. Create Deployment Guide

**Create file**: `{{CODE_GENERATION_BASE_PATH}}/DEPLOYMENT.md`

**Template**:
```markdown
#  Application - Deployment Guide

## Prerequisites

- Java 17 or higher
- Maven 3.8+
- Node.js 18+ and npm
- SQLite (embedded, no installation needed)

## Quick Start

### 1. Start Backend
```bash
cd {{CODE_GENERATION_BACKEND_OUTPUT}}
mvn spring-boot:run
```

Backend will start on **http://localhost:8080**

### 2. Start Frontend
```bash
cd {{CODE_GENERATION_FRONTEND_OUTPUT}}

# First time only
cp .env.example .env
npm install

# Start dev server
npm run dev
```

Frontend will start on **http://localhost:3000**

### 3. Access Application

Open browser: **http://localhost:3000**

## Test Credentials

### Admin User
- **Username**: `ADMIN001`
- **Password**: `password`
- **Access**: All administrative functions

### Regular User
- **Username**: `USER001`
- **Password**: `password`
- **Access**: Standard user functions

## Sample Data

### Transactions
- `TX0000000001` - Coffee Shop Purchase ($125.50)
- `TX0000000002` - Grocery Store ($89.99)

## Available Features

- ✅ **Login** (WP-001) - User authentication
- ✅ **Create User** (WP-002) - Add new users
- ✅ **View Transaction** (WP-003) - Transaction details
- ✅ **Delete User** (WP-004) - Remove users
- ✅ **Update User** (WP-005) - Modify user profiles

## Troubleshooting

### Backend won't start

**Port 8080 already in use**:
```bash
lsof -ti:8080 | xargs kill -9
```

**Database errors**:
- Check `backend/carddemo.db` exists
- Delete and restart to recreate: `rm backend/carddemo.db`

### Frontend won't start

**Port 3000 already in use**:
```bash
lsof -ti:3000 | xargs kill -9
```

**Dependencies missing**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Login fails

**Check password hash**:
- Passwords are uppercased before hashing
- Use BCrypt strength 10
- Verify seed data has correct hashes

**Check database**:
```bash
sqlite3 backend/carddemo.db "SELECT * FROM aws_m2_carddemo_usrsec_vsam_ksds;"
```

### API errors

**403 Forbidden**:
- CSRF should be disabled for REST APIs
- Check SecurityConfig

**CORS errors**:
- Frontend origin should be in CORS allowed origins
- Check SecurityConfig corsConfigurationSource

## Database

**Type**: SQLite (embedded)
**Location**: `backend/carddemo.db`
**Migrations**: Flyway (automatic on startup)
**Seed Data**: `backend/src/main/resources/data/seed-data.sql`

## Technical Stack

- **Backend**: Spring Boot 3.2.2, Java 17+
- **Frontend**: React 18, Vite, TypeScript
- **Database**: SQLite 3.45
- **Security**: Spring Security, BCrypt
- **API**: REST (JSON)

## Production Deployment

For production deployment:
1. Change database to PostgreSQL/MySQL
2. Enable CSRF for session-based auth
3. Configure proper CORS origins
4. Use environment variables for secrets
5. Enable HTTPS
6. Configure logging
7. Set up monitoring

## Support

For issues, check:
1. Backend logs: `backend/backend.log`
2. Frontend console: Browser DevTools (F12)
3. Database: `sqlite3 backend/carddemo.db`
```

### 9. Final Validation

**Run through complete user journey**:

1. ✅ Start backend and frontend
2. ✅ Login as ADMIN001
3. ✅ Navigate to admin menu
4. ✅ Create new user
5. ✅ Update user
6. ✅ View transaction
7. ✅ Delete user
8. ✅ Logout
9. ✅ Login as USER001
10. ✅ Navigate to main menu
11. ✅ View transaction
12. ✅ Logout

**All steps should work without errors.**

### 10. Update Progress Tracking

Update `{{CODE_GENERATION_STATUS}}`:

```json
{
  "phase": "Phase 5 - Code Generation",
  "currentStep": "5.6 - Integration Testing",
  "status": "completed",
  "integrationTesting": {
    "status": "completed",
    "testDate": "[timestamp]",
    "workpackagesTested": 5,
    "issuesFound": 8,
    "issuesFixed": 8,
    "deploymentReady": true
  }
}
```

---

## Quality Checklist

- [ ] Seed data script created and tested
- [ ] All workpackages tested end-to-end
- [ ] Login works with test users
- [ ] All CRUD operations work
- [ ] Frontend can call backend APIs
- [ ] No CORS errors
- [ ] No CSRF errors
- [ ] No enum mapping errors
- [ ] No SQL syntax errors
- [ ] Integration test report complete
- [ ] Deployment guide complete
- [ ] Test credentials documented
- [ ] All issues fixed and retested
- [ ] Progress tracking updated

---

## End of Phase 5.6 Specification
