import { useCallback, useEffect, useState } from "react";
import "./App.css";

const expenseOptions = {
  Food: [
    { emoji: "🍳", title: "Breakfast" },
    { emoji: "🍱", title: "Lunch" },
    { emoji: "🍽️", title: "Dinner" },
    { emoji: "☕", title: "Coffee" },
    { emoji: "🍪", title: "Snacks" },
  ],
  Transport: [
    { emoji: "🚆", title: "Train" },
    { emoji: "🚌", title: "Bus" },
    { emoji: "🚕", title: "Taxi" },
    { emoji: "⛽", title: "Fuel" },
    { emoji: "🅿️", title: "Parking" },
  ],
  Shopping: [
    { emoji: "👕", title: "Clothes" },
    { emoji: "👟", title: "Shoes" },
    { emoji: "💻", title: "Electronics" },
    { emoji: "🛒", title: "Shopping" },
    { emoji: "🏠", title: "Household Items" },
  ],
  Bills: [
    { emoji: "🏠", title: "Rent" },
    { emoji: "💡", title: "Electricity" },
    { emoji: "🔥", title: "Gas" },
    { emoji: "💧", title: "Water" },
    { emoji: "📱", title: "Phone" },
  ],
  Entertainment: [
    { emoji: "🎬", title: "Movie" },
    { emoji: "🎵", title: "Music" },
    { emoji: "🎮", title: "Games" },
    { emoji: "⚽", title: "Sports" },
    { emoji: "✈️", title: "Travel" },
  ],
  Health: [
    { emoji: "💊", title: "Medicine" },
    { emoji: "🩺", title: "Doctor" },
    { emoji: "🏋️", title: "Gym" },
    { emoji: "🛡️", title: "Insurance" },
  ],
  Study: [
    { emoji: "🎓", title: "Tuition" },
    { emoji: "📚", title: "Books" },
    { emoji: "💻", title: "Software" },
  ],
  Other: [{ emoji: "📦", title: "Other Expense" }],
};

const apiUrl = "http://127.0.0.1:8000";
const tokenStorageKey = "expense_access_token";
const userStorageKey = "expense_user";

function BrandTitle() {
  return (
    <span className="brand-title">
      <span className="brand-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" role="img">
          <path d="M4 7.5A2.5 2.5 0 0 1 6.5 5H17a2 2 0 0 1 2 2v1h.5A2.5 2.5 0 0 1 22 10.5v6A2.5 2.5 0 0 1 19.5 19h-13A4.5 4.5 0 0 1 2 14.5V9.5A2.5 2.5 0 0 1 4 7.5Z" />
          <path d="M17 13.5h3" />
          <path d="M6.5 5A2.5 2.5 0 0 0 4 7.5V8h13V7a2 2 0 0 0-2-2H6.5Z" />
        </svg>
      </span>
      Expense Tracker
    </span>
  );
}

function App() {
  const [token, setToken] = useState(
    () => localStorage.getItem(tokenStorageKey) || "",
  );
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem(userStorageKey);
    try {
      return savedUser ? JSON.parse(savedUser) : null;
    } catch {
      localStorage.removeItem(tokenStorageKey);
      localStorage.removeItem(userStorageKey);
      return null;
    }
  });
  const [authMode, setAuthMode] = useState("login");
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [registerUsername, setRegisterUsername] = useState("");
  const [registerEmail, setRegisterEmail] = useState("");
  const [registerPassword, setRegisterPassword] = useState("");
  const [authMessage, setAuthMessage] = useState("");
  const [authError, setAuthError] = useState("");
  const [authLoading, setAuthLoading] = useState(false);
  const [activeView, setActiveView] = useState("expenses");
  const [category, setCategory] = useState("Food");
  const [title, setTitle] = useState("");
  const [date, setDate] = useState("");
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");
  const [expenses, setExpenses] = useState([]);
  const [searchText, setSearchText] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editId, setEditId] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [adminUsers, setAdminUsers] = useState([]);
  const [adminActivities, setAdminActivities] = useState([]);
  const [adminLoading, setAdminLoading] = useState(false);
  const [adminError, setAdminError] = useState("");

  // Show titles for the selected category
  const titleList = expenseOptions[category];
  const isAdmin = user?.role === "admin";

  const readErrorMessage = async (response, defaultMessage) => {
    try {
      const data = await response.json();
      return data.detail || defaultMessage;
    } catch {
      return defaultMessage;
    }
  };

  // Clear the form
  const clearForm = useCallback(() => {
    setCategory("Food");
    setTitle("");
    setDate("");
    setAmount("");
    setDescription("");
    setEditId(null);
  }, []);

  const logout = useCallback(
    (message = "") => {
      const logoutMessage = typeof message === "string" ? message : "";

      localStorage.removeItem(tokenStorageKey);
      localStorage.removeItem(userStorageKey);
      setToken("");
      setUser(null);
      setExpenses([]);
      setChartData([]);
      setAdminUsers([]);
      setAdminActivities([]);
      setActiveView("expenses");
      setAuthMode("login");
      setAuthError(logoutMessage);
      setAuthMessage("");
      clearForm();
    },
    [clearForm],
  );

  const handleAuthFailure = useCallback(
    (status) => {
      if (status !== 401 && status !== 403) {
        return false;
      }

      const message =
        status === 401
          ? "Login expired. Please login again."
          : "You do not have permission. Please login again.";

      logout(message);
      return true;
    },
    [logout],
  );

  const handleLogout = async () => {
    try {
      await fetch(`${apiUrl}/logout`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
    } catch (err) {
      console.error(err);
    } finally {
      logout();
    }
  };

  const handleLogin = async (event) => {
    event.preventDefault();
    setAuthLoading(true);
    setAuthError("");
    setAuthMessage("");

    try {
      const formData = new URLSearchParams();
      formData.append("username", loginEmail);
      formData.append("password", loginPassword);

      const response = await fetch(`${apiUrl}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error(await readErrorMessage(response, "Login failed."));
      }

      const data = await response.json();
      localStorage.setItem(tokenStorageKey, data.access_token);
      localStorage.setItem(userStorageKey, JSON.stringify(data.user));
      setToken(data.access_token);
      setUser(data.user);
      setLoginPassword("");
      setActiveView("expenses");
      setAuthMessage("Login successful.");
    } catch (err) {
      setAuthError(err.message);
      console.error(err);
    } finally {
      setAuthLoading(false);
    }
  };

  const handleRegister = async (event) => {
    event.preventDefault();
    setAuthLoading(true);
    setAuthError("");
    setAuthMessage("");

    try {
      const response = await fetch(`${apiUrl}/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: registerUsername,
          email: registerEmail,
          password: registerPassword,
        }),
      });

      if (!response.ok) {
        throw new Error(
          await readErrorMessage(response, "Registration failed."),
        );
      }

      setRegisterUsername("");
      setRegisterEmail("");
      setRegisterPassword("");
      setAuthMode("login");
      setAuthMessage("Registration successful. Please login.");
    } catch (err) {
      setAuthError(err.message);
      console.error(err);
    } finally {
      setAuthLoading(false);
    }
  };

  // Load all records from the backend
  const loadExpenses = useCallback(async () => {
    if (!token) {
      return;
    }

    try {
      setLoading(true);
      setError("");
      // Send a request to get all records
      const response = await fetch(`${apiUrl}/expenses`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (handleAuthFailure(response.status)) {
          return;
        }
        throw new Error("Failed to fetch expenses.");
      }

      // Change the result into usable data
      const list = await response.json();
      setExpenses(list);
    } catch (err) {
      setError("Could not load expense records.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [handleAuthFailure, token]);
  // Load monthly totals for the chart
  const loadChartData = useCallback(async () => {
    if (!token) {
      return;
    }

    try {
      const response = await fetch(`${apiUrl}/expenses/trend`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (handleAuthFailure(response.status)) {
          return;
        }
        throw new Error("Failed to fetch monthly trend.");
      }

      const list = await response.json();
      setChartData(list);
    } catch (err) {
      console.error(err);
    }
  }, [handleAuthFailure, token]);
  // Load records and chart data when the page opens
  useEffect(() => {
    if (token && user) {
      loadExpenses();
      loadChartData();
    } else {
      setLoading(false);
    }
  }, [loadChartData, loadExpenses, token, user]);

  const handleAdminAccessError = useCallback(
    async (response, defaultMessage) => {
      if (response.status === 401) {
        logout("Login expired. Please login again.");
        return true;
      }

      if (response.status === 403) {
        setAdminError("Admin access required.");
        return true;
      }

      setAdminError(await readErrorMessage(response, defaultMessage));
      return true;
    },
    [logout],
  );

  // Load all users for admin
  const loadAdminUsers = useCallback(async () => {
    if (!token || !isAdmin) {
      setAdminError("Admin access required.");
      return;
    }

    try {
      setAdminLoading(true);
      setAdminError("");

      const response = await fetch(`${apiUrl}/admin/users`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        await handleAdminAccessError(response, "Failed to load users.");
        return;
      }

      const list = await response.json();
      setAdminUsers(list);
    } catch (err) {
      setAdminError("Failed to load users.");
      console.error(err);
    } finally {
      setAdminLoading(false);
    }
  }, [handleAdminAccessError, isAdmin, token]);

  // Load activity records for admin
  const loadAdminActivities = useCallback(async () => {
    if (!token || !isAdmin) {
      setAdminError("Admin access required.");
      return;
    }

    try {
      setAdminLoading(true);
      setAdminError("");

      const response = await fetch(`${apiUrl}/admin/activities`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        await handleAdminAccessError(response, "Failed to load activities.");
        return;
      }

      const list = await response.json();
      setAdminActivities(list);
    } catch (err) {
      setAdminError("Failed to load activities.");
      console.error(err);
    } finally {
      setAdminLoading(false);
    }
  }, [handleAdminAccessError, isAdmin, token]);

  const updateAdminUser = async (userId, userData) => {
    if (userId === user.id && userData.is_active === false) {
      setAdminError("You cannot deactivate your own admin account.");
      return;
    }

    try {
      setAdminError("");

      const response = await fetch(`${apiUrl}/admin/users/${userId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        await handleAdminAccessError(response, "Failed to update user.");
        return;
      }

      loadAdminUsers();
    } catch (err) {
      setAdminError("Failed to update user.");
      console.error(err);
    }
  };

  const deactivateAdminUser = async (userId) => {
    if (userId === user.id) {
      setAdminError("You cannot deactivate your own admin account.");
      return;
    }

    const confirmed = window.confirm(
      "Are you sure you want to deactivate this user?",
    );

    if (!confirmed) {
      return;
    }

    try {
      setAdminError("");

      const response = await fetch(`${apiUrl}/admin/users/${userId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        await handleAdminAccessError(response, "Failed to deactivate user.");
        return;
      }

      loadAdminUsers();
    } catch (err) {
      setAdminError("Failed to deactivate user.");
      console.error(err);
    }
  };

  useEffect(() => {
    if (activeView === "admin-users" && isAdmin) {
      loadAdminUsers();
    }

    if (activeView === "admin-activities" && isAdmin) {
      loadAdminActivities();
    }
  }, [activeView, isAdmin, loadAdminActivities, loadAdminUsers]);

  useEffect(() => {
    if (!isAdmin && activeView.startsWith("admin")) {
      setActiveView("expenses");
    }
  }, [activeView, isAdmin]);

  // Calculate the total amount
  const totalMoney = expenses.reduce(
    (sum, expense) => sum + Number(expense.amount),
    0,
  );
  // Calculate total amount for each category
  const categoryMoney = expenses.reduce((summary, expense) => {
    const itemCategory = expense.category;
    summary[itemCategory] =
      (summary[itemCategory] || 0) + Number(expense.amount);
    return summary;
  }, {});
  // Filter loaded expenses by the search box
  const searchKeyword = searchText.trim().toLowerCase();
  const filteredExpenses = searchKeyword
    ? expenses.filter((expense) => {
        const searchableText = [
          expense.title,
          expense.category,
          expense.description,
          expense.date,
          expense.amount,
        ]
          .join(" ")
          .toLowerCase();

        return searchableText.includes(searchKeyword);
      })
    : expenses;
  // Make the form data
  const buildFormData = () => {
    return {
      title: title,
      category: category,
      amount: Number(amount),
      expense_date: date,
      description: description,
    };
  };

  // Add a new record
  const addExpense = async () => {
    const payload = buildFormData();

    try {
      // Send new data with POST
      const response = await fetch(`${apiUrl}/expenses`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        if (handleAuthFailure(response.status)) {
          return;
        }
        throw new Error("Failed to add expense.");
      }

      clearForm();
      loadExpenses();
      loadChartData();
    } catch (err) {
      alert("Failed to add expense.");
      console.error(err);
    }
  };

  // Update one record
  const updateExpense = async () => {
    const payload = buildFormData();

    try {
      // Send updated data with PUT
      const response = await fetch(`${apiUrl}/expenses/${editId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        if (handleAuthFailure(response.status)) {
          return;
        }
        throw new Error("Failed to update expense.");
      }

      clearForm();
      loadExpenses();
      loadChartData();
    } catch (err) {
      alert("Failed to update expense.");
      console.error(err);
    }
  };

  // Check the form, then add or update
  const saveExpense = async () => {
    if (!title || !date || !amount) {
      alert("Please select a title and fill in date and amount.");
      return;
    }

    if (editId) {
      await updateExpense();
    } else {
      await addExpense();
    }
  };
  // Put old data back into the form
  const fillForm = (expense) => {
    setCategory(expense.category);
    setTitle(expense.title);
    setDate(String(expense.date).replaceAll("/", "-").slice(0, 10));
    setAmount(String(expense.amount));
    setDescription(expense.description || "");
    setEditId(expense.id);
  };

  // Delete one record
  const removeExpense = async (expenseId) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this expense?",
    );

    if (!confirmed) {
      return;
    }

    try {
      const response = await fetch(`${apiUrl}/expenses/${expenseId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (handleAuthFailure(response.status)) {
          return;
        }
        throw new Error("Failed to delete expense.");
      }

      if (editId === expenseId) {
        clearForm();
      }

      loadExpenses();
      loadChartData();
    } catch (err) {
      alert("Failed to delete expense.");
      console.error(err);
    }
  };

  // Find the biggest value for bar height
  const maxValue = Math.max(...chartData.map((item) => item.total), 1);

  if (!token || !user) {
    return (
      <div className="app auth-app">
        <section className="auth-card">
          <h1>
            <BrandTitle />
          </h1>

          <div className="auth-tabs">
            <button
              type="button"
              className={authMode === "login" ? "active" : ""}
              onClick={() => {
                setAuthMode("login");
                setAuthError("");
                setAuthMessage("");
              }}
            >
              Login
            </button>
            <button
              type="button"
              className={authMode === "register" ? "active" : ""}
              onClick={() => {
                setAuthMode("register");
                setAuthError("");
                setAuthMessage("");
              }}
            >
              Register
            </button>
          </div>

          {authMessage && <p className="auth-message">{authMessage}</p>}
          {authError && <p className="auth-error">{authError}</p>}

          {authMode === "login" ? (
            <form className="auth-form" onSubmit={handleLogin}>
              <label>Email</label>
              <input
                type="email"
                value={loginEmail}
                onChange={(e) => setLoginEmail(e.target.value)}
                placeholder="Enter your email"
                required
              />

              <label>Password</label>
              <input
                type="password"
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                placeholder="Enter your password"
                required
              />

              <button type="submit" disabled={authLoading}>
                {authLoading ? "Logging in..." : "Login"}
              </button>
            </form>
          ) : (
            <form className="auth-form" onSubmit={handleRegister}>
              <label>Username</label>
              <input
                type="text"
                value={registerUsername}
                onChange={(e) => setRegisterUsername(e.target.value)}
                placeholder="Choose a username"
                required
              />

              <label>Email</label>
              <input
                type="email"
                value={registerEmail}
                onChange={(e) => setRegisterEmail(e.target.value)}
                placeholder="Enter your email"
                required
              />

              <label>Password</label>
              <input
                type="password"
                value={registerPassword}
                onChange={(e) => setRegisterPassword(e.target.value)}
                placeholder="Choose a password"
                required
              />

              <button type="submit" disabled={authLoading}>
                {authLoading ? "Registering..." : "Register"}
              </button>
            </form>
          )}
        </section>
      </div>
    );
  }

  return (
    <div className="app">
      {/* Top area: total and category summary */}
      <header className="top-section">
        <div className="dashboard-header">
          <h1>
            <BrandTitle />
          </h1>
          <div className="user-box">
            <span>
              {user.username} ({user.email}) - {user.role}
            </span>
            <button type="button" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>
        <div className="view-tabs">
          <button
            type="button"
            className={activeView === "expenses" ? "active" : ""}
            onClick={() => setActiveView("expenses")}
          >
            Expenses
          </button>
          {isAdmin && (
            <>
              <button
                type="button"
                className={activeView === "admin-users" ? "active" : ""}
                onClick={() => setActiveView("admin-users")}
              >
                Admin Users
              </button>
              <button
                type="button"
                className={activeView === "admin-activities" ? "active" : ""}
                onClick={() => setActiveView("admin-activities")}
              >
                Admin Activities
              </button>
            </>
          )}
        </div>
        {activeView === "expenses" && (
          <div className="summary-cards">
            <div className="card">
              <h3>Total Expense</h3>
              <p>${totalMoney.toFixed(2)}</p>
            </div>
            <div className="card">
              <h3>Category Summary</h3>
              {Object.keys(categoryMoney).length === 0 ? (
                <p>No data yet</p>
              ) : (
                <div className="summary-list">
                  {Object.entries(categoryMoney).map(([category, value]) => (
                    <p key={category}>
                      <strong>{category}:</strong> ${value.toFixed(2)}
                    </p>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </header>

      {/* Middle area: list on the left, form on the right */}
      {activeView === "expenses" && (
        <main className="main-content">
          {/* Expense record list */}
          <section className="expense-list-section">
            <h2>Expense Records</h2>
            <input
              className="search-input"
              type="text"
              placeholder="Search expenses..."
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />

            {loading && <p>Loading expenses...</p>}
            {error && <p>{error}</p>}

            {!loading && !error && expenses.length === 0 && (
              <p>No expense records found.</p>
            )}

            {!loading &&
              !error &&
              expenses.length > 0 &&
              filteredExpenses.length === 0 && (
                <p>No matching expenses found.</p>
              )}

            {!loading &&
              !error &&
              filteredExpenses.map((expense) => (
                <div key={expense.id} className="expense-item">
                  <p>
                    <strong>Title:</strong> {expense.title}
                  </p>
                  <p>
                    <strong>Date:</strong> {expense.date}
                  </p>
                  <p>
                    <strong>Category:</strong> {expense.category}
                  </p>
                  <p>
                    <strong>Amount:</strong> $
                    {Number(expense.amount).toFixed(2)}
                  </p>
                  <p>
                    <strong>Description:</strong>{" "}
                    {expense.description || "No description"}
                  </p>
                  <div className="button-group">
                    <button type="button" onClick={() => fillForm(expense)}>
                      Edit
                    </button>
                    <button
                      type="button"
                      onClick={() => removeExpense(expense.id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
          </section>

          {/* Add / edit form */}
          <section className="form-section">
            <h2>{editId ? "Edit Expense" : "Add Expense"}</h2>

            <label>Category</label>
            <div className="category-grid">
              {Object.keys(expenseOptions).map((itemCategory) => (
                <button
                  key={itemCategory}
                  type="button"
                  className={`category-btn ${itemCategory === category ? "active" : ""}`}
                  onClick={() => {
                    setCategory(itemCategory);
                    setTitle("");
                  }}
                >
                  {itemCategory}
                </button>
              ))}
            </div>

            <label>Title</label>
            <div className="title-grid">
              {titleList.map((item) => (
                <div
                  key={item.title}
                  className={`title-card ${item.title === title ? "selected" : ""}`}
                  onClick={() => setTitle(item.title)}
                >
                  <div className="emoji">{item.emoji}</div>
                  <div className="title-text">{item.title}</div>
                </div>
              ))}
            </div>

            {title && <p className="selected-title">Selected Title: {title}</p>}

            <label>Date</label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />

            <label>Amount</label>
            <input
              type="number"
              step="0.01"
              min="0"
              placeholder="Enter amount"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />

            <label>Description</label>
            <textarea
              placeholder="Enter description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            ></textarea>

            <button className="add-btn" type="button" onClick={saveExpense}>
              {editId ? "Update Expense" : "Add Expense"}
            </button>

            {editId && (
              <button className="add-btn" type="button" onClick={clearForm}>
                Cancel Edit
              </button>
            )}
          </section>
        </main>
      )}

      {activeView === "expenses" && (
        <section className="bottom-section">
          <h2>Monthly Trend Chart</h2>
          {chartData.length === 0 ? (
            <div className="chart-box">No trend data yet</div>
          ) : (
            <div className="trend-chart">
              {chartData.map((item) => {
                // Set bar height by the biggest value
                const barHeight = (item.total / maxValue) * 180;

                return (
                  <div key={item.month} className="trend-item">
                    <div className="trend-value">${item.total.toFixed(2)}</div>
                    <div className="trend-bar-wrapper">
                      <div
                        className="trend-bar"
                        style={{ height: `${barHeight}px` }}
                      ></div>
                    </div>
                    <div className="trend-label">{item.month}</div>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      )}

      {activeView === "admin-users" && (
        <section className="admin-section">
          <h2>Admin Users</h2>
          {adminLoading && <p>Loading admin users...</p>}
          {adminError && <p className="admin-error">{adminError}</p>}
          {!adminLoading && adminUsers.length === 0 && !adminError && (
            <p>No users found.</p>
          )}
          {adminUsers.length > 0 && (
            <div className="table-wrap">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Active</th>
                    <th>Created At</th>
                    <th>Actions</th>
                  </tr>
                </thead>
	                <tbody>
		                  {adminUsers.map((adminUser) => {
		                    const isCurrentUser = adminUser.id === user.id;

                    return (
                      <tr key={adminUser.id}>
                        <td>{adminUser.id}</td>
                        <td>{adminUser.username}</td>
                        <td>{adminUser.email}</td>
                        <td>
	                          <select
	                            value={adminUser.role}
	                            onChange={(e) =>
	                              updateAdminUser(adminUser.id, {
	                                role: e.target.value,
                              })
                            }
                          >
                            <option value="user">user</option>
                            <option value="admin">admin</option>
                          </select>
                        </td>
                        <td>
                          <select
                            value={String(adminUser.is_active)}
                            onChange={(e) =>
                              updateAdminUser(adminUser.id, {
                                is_active: e.target.value === "true",
                              })
                            }
                          >
                            <option value="true">active</option>
                            {!isCurrentUser && (
                              <option value="false">inactive</option>
                            )}
                          </select>
                        </td>
                        <td>{adminUser.created_at}</td>
                        <td>
                          <button
                            type="button"
                            disabled={isCurrentUser}
                            onClick={() => deactivateAdminUser(adminUser.id)}
                          >
                            {isCurrentUser ? "Current User" : "Deactivate"}
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      {activeView === "admin-activities" && (
        <section className="admin-section">
          <h2>Admin Activities</h2>
          {adminLoading && <p>Loading activities...</p>}
          {adminError && <p className="admin-error">{adminError}</p>}
          {!adminLoading && adminActivities.length === 0 && !adminError && (
            <p>No activities found.</p>
          )}
          {adminActivities.length > 0 && (
            <div className="table-wrap">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>User ID</th>
                    <th>Action</th>
                    <th>Detail</th>
                    <th>Created At</th>
                  </tr>
                </thead>
                <tbody>
                  {adminActivities.map((activity) => (
                    <tr key={activity.id}>
                      <td>{activity.id}</td>
                      <td>{activity.user_id}</td>
                      <td>{activity.action}</td>
                      <td>{activity.detail || "No detail"}</td>
                      <td>{activity.created_at}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}
    </div>
  );
}

export default App;
