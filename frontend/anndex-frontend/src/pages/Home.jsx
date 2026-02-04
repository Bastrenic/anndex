import { Box, Button, Divider, SvgIcon, TextField, Typography } from '@mui/material';
import { Fragment } from 'react';
import anndexImg from '../assets/anndex.png'
import axios from 'axios';
import { API_URL } from '../App';

const handleSubmit = (event) => {
  event.preventDefault();
  const formData = new FormData(event.currentTarget);
  axios.get(`${API_URL}/product?q=${formData.get('search-query')}`)
    .then((response) => {
      console.log(response)
    })
}

export default function Home() {
  return (
    <Fragment>
      <Box 
        sx={{
          height: '100vh', 
          width: '100vw', 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center',
          justifyContent: 'center',
          background: '#bcc5cf'
        }}
      >
        <Box
          component="img"
          sx={{
            width: '600px',
            height: '600px'
          }}
          src={anndexImg}
        
        />
        <Box 
          sx={{
            background: '#773da1', 
            maxWidth: '700px',
            height: '15%', 
            width: '80%',
            borderRadius: '32px', 
            display: 'flex', 
            justifyContent: 'center',
          }}
        >
          <form 
            onSubmit={handleSubmit}
            style={{
              height: '100%', 
              width: '80%', 
              display: 'flex', 
              alignItems: 'center'
            }}
          >
            <TextField 
              variant="outlined"
              placeholder="Start Searching!"
              id='search-query'
              name='search-query'
              sx={{
                width: "100%",
                "& .MuiOutlinedInput-root": {
                  borderRadius: '16px',
                  "& fieldset": {
                    borderColor: "#ba87ca",
                  },
                  "&:hover fieldset": {
                    borderColor: "#ba87ca", 
                  },
                  "&.Mui-focused fieldset": {
                    borderColor: "#ba87ca",
                  },
                },
                "& .MuiOutlinedInput-input": {
                  color: "#dcd7dd",
                  padding: "3%", 
                  fontSize: "1.3em",
                },
              }}
            />
          </form>
        </Box>
      </Box>
    </Fragment>
  )

}