## SQL Vulnerability Checklist

-----

### SQLI-001: Dynamic Query String Concatenation

Checks if untrusted user-supplied input (from parameters, form fields, URLs, cookies, etc.) is directly concatenated or formatted into an SQL query string. This is the root cause of most SQL injection vulnerabilities.

**Enabled Attack Techniques:**

  * Classic (Inband)
  * Error-Based
  * UNION-Based
  * Blind (Boolean-Based)
  * Blind (Time-Based)
  * Stacked Queries

**Example Vulnerable Code:**

```java
String query = "SELECT * FROM users WHERE user_name = '" + request.getParameter("customerName") + "';";
```

**Recommended Solution:**
Refactor the code to use **Prepared Statements (with Parameterized Queries)**. User input must be bound as a parameter, which ensures the database engine treats it strictly as data and not as executable code. This is the primary defense.

-----

### SQLI-002: Dynamic Table/Column Concatenation

Checks if user input is used to define structural parts of a query, such as table names, column names, or sort order (e.g., `ORDER BY`). Prepared Statements cannot parameterize these parts of a query.

**Enabled Attack Techniques:**

  * Classic (Inband)
  * Error-Based

**Example Vulnerable Code:**

```java
String sortByColumn = request.getParameter("sort");
String query = "SELECT * FROM products ORDER BY " + sortByColumn;
```

**Recommended Solution:**
Do not concatenate this input directly. The **only** safe solution is to validate the user input against a strict **allow-list** of known, safe, hard-coded values. If the input is not on the list, the query should be rejected or a safe default value used.

-----

### SQLI-003: Insecure Stored Procedure

Checks if a Stored Procedure, while called 'safely' from the application, internally builds dynamic SQL strings (e.g., using `EXEC`, `sp_executesql`) with its input parameters. This re-introduces the vulnerability within the database itself.

**Enabled Attack Techniques:**

  * Classic (Inband)
  * Error-Based
  * Blind (Boolean/Time)
  * Stacked Queries

**Example Vulnerable Code:**

```sql
/* T-SQL Example */
CREATE PROCEDURE sp_get_user @name VARCHAR(100)
AS
BEGIN
    /* VULNERABLE: Dynamic SQL string execution */
    EXEC('SELECT * FROM users WHERE name = ''' + @name + '''');
END
```

**Recommended Solution:**
Rewrite the Stored Procedure to be non-dynamic. The procedure should use its input parameters directly in its SQL logic (e.g., `SELECT * FROM users WHERE name = @name;`) without concatenating them into a new executable string.

-----

### SQLI-004: Second-Order (Stored) SQL Injection

Checks if user input is 'safely' stored in the database (e.g., a username, profile comment) and then later retrieved and used in a *different* query dynamically, trusting it because it came 'from the database'.

**Enabled Attack Techniques:**

  * Second-Order

**Example Vulnerable Code:**

```java
// 1. User registers with name "admin'--". This is stored.
// 2. Later, a different, vulnerable function builds a query:
String userNameFromDB = ...; /* Fetches "admin'--" */
String query = "UPDATE user_prefs SET theme = 'dark' WHERE username = '" + userNameFromDB + "';";
```

**Recommended Solution:**
Treat all data as untrusted, even if it is retrieved from your own database. Apply the same primary defenses **(Prepared Statements or Allow-list Validation)** to data retrieved from the database *before* using it in a new query.

-----

### SQLI-005: Insecure Escaping / Block-list Filtering

Checks if the code attempts to 'sanitize' user input by escaping or removing special characters (e.g., replacing `'` with `''`, removing `--`, or stripping `;`) before concatenating it into a query. This is a frail, unreliable defense.

**Enabled Attack Techniques:**

  * Classic (Inband)
  * Error-Based

**Example Vulnerable Code:**

```java
String safeUser = request.getParameter("user").replace("'", "''");
String query = "SELECT * FROM users WHERE username = '" + safeUser + "';";
```

**Recommended Solution:**
This method is **strongly discouraged**. Remove the flawed escaping logic entirely. The correct solution is to use **Prepared Statements (with Parameterized Queries)**.

-----

### SQLI-006: Excessive Database Privileges

Checks the database user/role that the application uses to connect. Does this user have administrative privileges (e.g., `db_owner`, `SA`, `root`), permissions to run OS commands (`xp_cmdshell`), or broad `DROP`/`CREATE`/`SHUTDOWN` permissions?

**Enabled Attack Techniques:**

  * Out-of-Band (OOB)
  * Stacked Queries (e.g., `DROP TABLE`)
  * Privilege Escalation

**Example Vulnerable Code:**

```sql
-- Connection string: "User ID=sa;Password=..."
-- Or code executes: "GRANT DBA TO web_app_user;"
```

**Recommended Solution:**
Apply the **Principle of Least Privilege**. Create a dedicated, low-privilege database user for the application. This user should *only* have the specific permissions it needs (e.g., `SELECT`, `INSERT` on specific tables) and be denied all administrative, OS-level, or file-system-access commands.

-----

### SQLI-007: Improper Error Handling (Information Leak)

Checks if detailed database errors (e.g., 'Unclosed quotation mark', 'Syntax error converting varchar') are sent back to the client/user. This is not an injection flaw itself, but it provides attackers with critical information to refine their attacks.

**Enabled Attack Techniques:**

  * Error-Based

**Example Vulnerable Code:**

```java
try { 
    // ... database logic ... 
} catch (SQLException ex) {
    /* VULNERABLE: Sending detailed error to user */
    response.getWriter().print(ex.getMessage());
}
```

**Recommended Solution:**
Implement generic error handling. Never send detailed database or system errors to the user. Log the detailed error on the server for debugging and return a generic, non-informative error message (e.g., 'An unexpected error occurred. Please try again later.').