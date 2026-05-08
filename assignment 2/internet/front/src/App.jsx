import { useEffect, useState } from 'react'
import './App.css'

const expenseOptions = {
  Food: [
    { emoji: '🍳', title: 'Breakfast' },
    { emoji: '🍱', title: 'Lunch' },
    { emoji: '🍽️', title: 'Dinner' },
    { emoji: '☕', title: 'Coffee' },
    { emoji: '🍪', title: 'Snacks' },
  ],
  Transport: [
    { emoji: '🚆', title: 'Train' },
    { emoji: '🚌', title: 'Bus' },
    { emoji: '🚕', title: 'Taxi' },
    { emoji: '⛽', title: 'Fuel' },
    { emoji: '🅿️', title: 'Parking' },
  ],
  Shopping: [
    { emoji: '👕', title: 'Clothes' },
    { emoji: '👟', title: 'Shoes' },
    { emoji: '💻', title: 'Electronics' },
    { emoji: '🛒', title: 'Shopping' },
    { emoji: '🏠', title: 'Household Items' },
  ],
  Bills: [
    { emoji: '🏠', title: 'Rent' },
    { emoji: '💡', title: 'Electricity' },
    { emoji: '🔥', title: 'Gas' },
    { emoji: '💧', title: 'Water' },
    { emoji: '📱', title: 'Phone' },
  ],
  Entertainment: [
    { emoji: '🎬', title: 'Movie' },
    { emoji: '🎵', title: 'Music' },
    { emoji: '🎮', title: 'Games' },
    { emoji: '⚽', title: 'Sports' },
    { emoji: '✈️', title: 'Travel' },
  ],
  Health: [
    { emoji: '💊', title: 'Medicine' },
    { emoji: '🩺', title: 'Doctor' },
    { emoji: '🏋️', title: 'Gym' },
    { emoji: '🛡️', title: 'Insurance' },
  ],
  Study: [
    { emoji: '🎓', title: 'Tuition' },
    { emoji: '📚', title: 'Books' },
    { emoji: '💻', title: 'Software' },
  ],
  Other: [
    { emoji: '📦', title: 'Other Expense' },
  ],
}

const apiUrl = 'http://127.0.0.1:8000'

function App() {
  const [category, setCategory] = useState('Food')
  const [title, setTitle] = useState('')
  const [date, setDate] = useState('')
  const [amount, setAmount] = useState('')
  const [description, setDescription] = useState('')
  const [expenses, setExpenses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [editId, setEditId] = useState(null)
  const [chartData, setChartData] = useState([])

  // Show titles for the selected category
  const titleList = expenseOptions[category]

  // Load all records from the backend
  const loadExpenses = async () => {
    try {
      setLoading(true)
      setError('')
      // Send a request to get all records
      const response = await fetch(`${apiUrl}/expenses`)

      if (!response.ok) {
        throw new Error('Failed to fetch expenses.')
      }

      // Change the result into usable data
      const list = await response.json()
      setExpenses(list)
    } catch (err) {
      setError('Could not load expense records.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }
  // Load monthly totals for the chart
  const loadChartData = async () => {
    try {
      const response = await fetch(`${apiUrl}/expenses/trend`)

      if (!response.ok) {
        throw new Error('Failed to fetch monthly trend.')
      }

      const list = await response.json()
      setChartData(list)
    } catch (err) {
      console.error(err)
    }
  }
  // Load records and chart data when the page opens
  useEffect(() => {
    loadExpenses()
    loadChartData()
  }, [])
  // Calculate the total amount
  const totalMoney = expenses.reduce((sum, expense) => sum + Number(expense.amount), 0)
  // Calculate total amount for each category
  const categoryMoney = expenses.reduce((summary, expense) => {
    const itemCategory = expense.category
    summary[itemCategory] = (summary[itemCategory] || 0) + Number(expense.amount)
    return summary
  }, {})
  // Make the form data
  const buildFormData = () => {
    return {
      title: title,
      category: category,
      amount: Number(amount),
      expense_date: date,
      description: description,
    }
  }

  // Add a new record
  const addExpense = async () => {
    const payload = buildFormData()

    try {
      // Send new data with POST
      const response = await fetch(`${apiUrl}/expenses`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error('Failed to add expense.')
      }

      clearForm()
      loadExpenses()
      loadChartData()
    } catch (err) {
      alert('Failed to add expense.')
      console.error(err)
    }
  }

  // Update one record
  const updateExpense = async () => {
    const payload = buildFormData()

    try {
      // Send updated data with PUT
      const response = await fetch(`${apiUrl}/expenses/${editId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error('Failed to update expense.')
      }

      clearForm()
      loadExpenses()
      loadChartData()
    } catch (err) {
      alert('Failed to update expense.')
      console.error(err)
    }
  }

  // Check the form, then add or update
  const saveExpense = async () => {
    if (!title || !date || !amount) {
      alert('Please select a title and fill in date and amount.')
      return
    }

    if (editId) {
      await updateExpense()
    } else {
      await addExpense()
    }
  }
  // Clear the form
  const clearForm = () => {
    setCategory('Food')
    setTitle('')
    setDate('')
    setAmount('')
    setDescription('')
    setEditId(null)
  }

  // Put old data back into the form
  const fillForm = (expense) => {
    setCategory(expense.category)
    setTitle(expense.title)
    setDate(String(expense.date).replaceAll('/', '-').slice(0, 10))
    setAmount(String(expense.amount))
    setDescription(expense.description || '')
    setEditId(expense.id)
  }

  // Delete one record
  const removeExpense = async (expenseId) => {
    const confirmed = window.confirm('Are you sure you want to delete this expense?')

    if (!confirmed) {
      return
    }

    try {
      const response = await fetch(`${apiUrl}/expenses/${expenseId}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error('Failed to delete expense.')
      }

      if (editId === expenseId) {
        clearForm()
      }

      loadExpenses()
      loadChartData()
    } catch (err) {
      alert('Failed to delete expense.')
      console.error(err)
    }
  }

  // Find the biggest value for bar height
  const maxValue = Math.max(...chartData.map((item) => item.total), 1)

  return (
    <div className="app">
      {/* Top area: total and category summary */}
      <header className="top-section">
        <h1>Expense Tracker</h1>
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
      </header>

      {/* Middle area: list on the left, form on the right */}
      <main className="main-content">
        {/* Expense record list */}
        <section className="expense-list-section">
          <h2>Expense Records</h2>

          {loading && <p>Loading expenses...</p>}
          {error && <p>{error}</p>}

          {!loading && !error && expenses.length === 0 && (
            <p>No expense records found.</p>
          )}

          {!loading && !error && expenses.map((expense) => (
            <div key={expense.id} className="expense-item">
              <p><strong>Title:</strong> {expense.title}</p>
              <p><strong>Date:</strong> {expense.date}</p>
              <p><strong>Category:</strong> {expense.category}</p>
              <p><strong>Amount:</strong> ${Number(expense.amount).toFixed(2)}</p>
              <p><strong>Description:</strong> {expense.description || 'No description'}</p>
              <div className="button-group">
                <button type="button" onClick={() => fillForm(expense)}>Edit</button>
                <button type="button" onClick={() => removeExpense(expense.id)}>Delete</button>
              </div>
            </div>
          ))}
        </section>

        {/* Add / edit form */}
        <section className="form-section">
          <h2>{editId ? 'Edit Expense' : 'Add Expense'}</h2>

          <label>Category</label>
          <div className="category-grid">
            {Object.keys(expenseOptions).map((itemCategory) => (
              <button
                key={itemCategory}
                type="button"
                className={`category-btn ${itemCategory === category ? 'active' : ''}`}
                onClick={() => {
                  setCategory(itemCategory)
                  setTitle('')
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
                className={`title-card ${item.title === title ? 'selected' : ''}`}
                onClick={() => setTitle(item.title)}
              >
                <div className="emoji">{item.emoji}</div>
                <div className="title-text">{item.title}</div>
              </div>
            ))}
          </div>

          {title && <p className="selected-title">Selected Title: {title}</p>}

          <label>Date</label>
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />

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
            {editId ? 'Update Expense' : 'Add Expense'}
          </button>

          {editId && (
            <button className="add-btn" type="button" onClick={clearForm}>
              Cancel Edit
            </button>
          )}
        </section>
      </main>

      {/* Bottom area: monthly trend chart */}
      <section className="bottom-section">
        <h2>Monthly Trend Chart</h2>
        {chartData.length === 0 ? (
          <div className="chart-box">No trend data yet</div>
        ) : (
          <div className="trend-chart">
            {chartData.map((item) => {
              // Set bar height by the biggest value
              const barHeight = (item.total / maxValue) * 180

              return (
                <div key={item.month} className="trend-item">
                  <div className="trend-value">${item.total.toFixed(2)}</div>
                  <div className="trend-bar-wrapper">
                    <div className="trend-bar" style={{ height: `${barHeight}px` }}></div>
                  </div>
                  <div className="trend-label">{item.month}</div>
                </div>
              )
            })}
          </div>
        )}
      </section>
    </div>
  )
}

export default App