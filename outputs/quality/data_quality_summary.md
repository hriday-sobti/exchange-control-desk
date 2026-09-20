# Data Quality Audit Report

**Audit Date:** 2026-09-20T11:55:31.395550+00:00  
**Overall Data Quality Score:** **100.0 / 100.0**  
**Total Records Evaluated:** 101,487  
**Clean Records Loaded:** 101,487 (100.00%)  
**Quarantined Records:** 0  

---

## Dimension Breakdown

| Dimension | Weight | Dimension Score (%) |
| :--- | :--- | :--- |
| **Completeness** | 25% | 100.0% |
| **Validity** | 20% | 100.0% |
| **Consistency** | 20% | 100.0% |
| **Uniqueness** | 15% | 100.0% |
| **Referential Integrity** | 10% | 100.0% |
| **Timeliness** | 10% | 100.0% |

---

## Detailed Check Results

| Check ID | Dimension | Field | Records Checked | Failed | Failure Rate | Status | Severity |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `CHK_CMP_TRANSACTION_ID` | completeness | `transaction_id` | 101,487 | 0 | 0.0000% | **PASSED** | CRITICAL |
| `CHK_CMP_USER_ID` | completeness | `user_id` | 101,487 | 0 | 0.0000% | **PASSED** | CRITICAL |
| `CHK_CMP_ASSET_ID` | completeness | `asset_id` | 101,487 | 0 | 0.0000% | **PASSED** | CRITICAL |
| `CHK_CMP_TIMESTAMP` | completeness | `timestamp` | 101,487 | 0 | 0.0000% | **PASSED** | CRITICAL |
| `CHK_CMP_GROSS_VALUE` | completeness | `gross_value` | 101,487 | 0 | 0.0000% | **PASSED** | CRITICAL |
| `CHK_CMP_QUANTITY` | completeness | `quantity` | 101,487 | 0 | 0.0000% | **PASSED** | CRITICAL |
| `CHK_CMP_PRICE` | completeness | `price` | 101,487 | 0 | 0.0000% | **PASSED** | CRITICAL |
| `CHK_CMP_STATUS` | completeness | `status` | 101,487 | 0 | 0.0000% | **PASSED** | CRITICAL |
| `CHK_VAL_TX_TYPE` | validity | `transaction_type` | 101,487 | 0 | 0.0000% | **PASSED** | CRITICAL |
| `CHK_VAL_POSITIVE_VALS` | validity | `gross_value,quantity` | 101,487 | 0 | 0.0000% | **PASSED** | CRITICAL |
| `CHK_VAL_NON_NEG_FEE` | validity | `fee` | 101,487 | 0 | 0.0000% | **PASSED** | HIGH |
| `CHK_CON_MATH_BALANCE` | consistency | `gross_value` | 101,487 | 0 | 0.0000% | **PASSED** | HIGH |
| `CHK_UNQ_TX_ID` | uniqueness | `transaction_id` | 101,487 | 0 | 0.0000% | **PASSED** | CRITICAL |
| `CHK_REF_USER_EXISTS` | referential_integrity | `user_id` | 101,487 | 0 | 0.0000% | **PASSED** | CRITICAL |
| `CHK_REF_ASSET_EXISTS` | referential_integrity | `asset_id` | 101,487 | 0 | 0.0000% | **PASSED** | CRITICAL |
| `CHK_TIM_FUTURE_DATED` | timeliness | `timestamp` | 101,487 | 0 | 0.0000% | **PASSED** | MEDIUM |
