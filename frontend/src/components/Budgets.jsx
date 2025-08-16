import React, { useState } from 'react'
import { 
  Paper, 
  Typography, 
  Button, 
  TextField, 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Card,
  CardContent,
  CardActions
} from '@mui/material'

function Budgets() {
  const [open, setOpen] = useState(false)
  const [budgets, setBudgets] = useState([])

  const handleCreateBudget = () => {
    // TODO: Implement budget creation
    setOpen(false)
  }

  return (
    <div>
      <Typography variant="h4" gutterBottom>
        Budgets
      </Typography>
      <Button 
        variant="contained" 
        onClick={() => setOpen(true)}
        sx={{ mb: 3 }}
      >
        Create New Budget
      </Button>
      
      <Grid container spacing={3}>
        {budgets.length === 0 ? (
          <Grid item xs={12}>
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" color="textSecondary">
                No budgets created yet
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Create your first budget to start managing your finances
              </Typography>
            </Paper>
          </Grid>
        ) : (
          budgets.map((budget) => (
            <Grid item xs={12} md={6} lg={4} key={budget.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6">{budget.name}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    {budget.type}
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button size="small">View</Button>
                  <Button size="small">Edit</Button>
                </CardActions>
              </Card>
            </Grid>
          ))
        )}
      </Grid>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Budget</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Budget Name"
            fullWidth
            variant="outlined"
            sx={{ mb: 2 }}
          />
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Budget Type</InputLabel>
            <Select label="Budget Type">
              <MenuItem value="family">Family</MenuItem>
              <MenuItem value="unbox">Unbox</MenuItem>
              <MenuItem value="neoschool">Neoschool</MenuItem>
              <MenuItem value="personal">Personal</MenuItem>
            </Select>
          </FormControl>
          <FormControl fullWidth>
            <InputLabel>Default Currency</InputLabel>
            <Select label="Default Currency">
              <MenuItem value="GEL">GEL</MenuItem>
              <MenuItem value="USD">USD</MenuItem>
              <MenuItem value="EUR">EUR</MenuItem>
              <MenuItem value="UAH">UAH</MenuItem>
              <MenuItem value="USDT">USDT</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateBudget} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>
    </div>
  )
}

export default Budgets