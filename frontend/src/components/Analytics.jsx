import React from 'react'
import { Typography, Paper, Grid, Card, CardContent } from '@mui/material'

function Analytics() {
  return (
    <div>
      <Typography variant="h4" gutterBottom>
        Analytics & Reports
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Monthly Summary
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Income vs Expenses chart will be displayed here
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Category Breakdown
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Expense categories pie chart will be displayed here
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Currency Exchange Rates
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Current exchange rates for GEL, USD, EUR, UAH, USDT
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Export Data
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Export options: CSV, Excel, PDF reports
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </div>
  )
}

export default Analytics