import { useState } from 'react';

// material-ui
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import InputAdornment from '@mui/material/InputAdornment';
import IconButton from '@mui/material/IconButton';
import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';
import Link from '@mui/material/Link';
import { styled } from '@mui/material/styles';

// icons
import EyeOutlined from '@ant-design/icons/EyeOutlined';
import EyeInvisibleOutlined from '@ant-design/icons/EyeInvisibleOutlined';

// ================================|| STYLED COMPONENTS ||================================ //

const Container = styled(Box)({
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  minHeight: '100vh',
  width: '100vw',
  background: 'linear-gradient(135deg, #1e5ba8 0%, #2563c4 100%)',
  position: 'relative',
  overflow: 'hidden',
  padding: '40px 20px'
});

const MainCard = styled(Box)(({ theme }) => ({
  display: 'flex',
  width: '100%',
  maxWidth: '900px',
  height: '500px',
  background: '#fff',
  borderRadius: '20px',
  boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
  overflow: 'hidden',
  position: 'relative',
  zIndex: 10,
  [theme.breakpoints.down('md')]: {
    flexDirection: 'column',
    height: 'auto',
    maxWidth: '450px'
  }
}));

const LeftSection = styled(Box)(({ theme }) => ({
  flex: 1,
  background: 'linear-gradient(135deg, #1e5ba8 0%, #2563c4 100%)',
  padding: '60px 40px',
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  position: 'relative',
  overflow: 'hidden',
  [theme.breakpoints.down('md')]: {
    padding: '40px 30px',
    minHeight: '250px'
  }
}));

const RightSection = styled(Box)(({ theme }) => ({
  flex: 1,
  background: '#fff',
  padding: '50px 45px',
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  [theme.breakpoints.down('md')]: {
    padding: '40px 30px'
  }
}));

// Geometric decorative elements
const GeometricSquare = styled(Box)(({ size = '150px', top, left, opacity = 0.1 }) => ({
  position: 'absolute',
  width: size,
  height: size,
  background: `rgba(255, 255, 255, ${opacity})`,
  borderRadius: '20px',
  top: top,
  left: left,
  transform: 'rotate(45deg)'
}));

const Sphere = styled(Box)(({ theme }) => ({
  position: 'absolute',
  width: '200px',
  height: '200px',
  borderRadius: '50%',
  background: 'radial-gradient(circle at 30% 30%, #4a8fe7, #1e5ba8)',
  boxShadow: '0 20px 60px rgba(0, 0, 0, 0.4), inset -20px -20px 40px rgba(0, 0, 0, 0.2)',
  bottom: '-50px',
  left: '50%',
  transform: 'translateX(-50%)',
  [theme.breakpoints.down('md')]: {
    width: '150px',
    height: '150px',
    bottom: '-40px'
  }
}));

const StyledTextField = styled(TextField)({
  '& .MuiOutlinedInput-root': {
    borderRadius: '8px',
    background: '#f8f9fa',
    '& fieldset': {
      borderColor: '#e0e0e0'
    },
    '&:hover fieldset': {
      borderColor: '#2563c4'
    },
    '&.Mui-focused fieldset': {
      borderColor: '#2563c4'
    }
  },
  '& .MuiInputBase-input': {
    padding: '12px 14px'
  }
});

const SignInButton = styled(Button)({
  padding: '12px',
  fontSize: '15px',
  fontWeight: 600,
  textTransform: 'none',
  borderRadius: '8px',
  background: '#2563c4',
  color: '#fff',
  boxShadow: '0 4px 12px rgba(37, 99, 196, 0.4)',
  '&:hover': {
    background: '#1e5ba8',
    boxShadow: '0 6px 16px rgba(37, 99, 196, 0.5)'
  }
});

const OutlinedButton = styled(Button)({
  padding: '11px',
  fontSize: '15px',
  fontWeight: 600,
  textTransform: 'none',
  borderRadius: '8px',
  background: '#fff',
  color: '#666',
  border: '1px solid #d0d0d0',
  '&:hover': {
    background: '#f8f9fa',
    borderColor: '#2563c4'
  }
});

// ================================|| JWT - LOGIN V3 ||================================ //

export default function LoginV3() {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Login attempt (UI only):', { email, password: '***', rememberMe });
    alert('This is UI demo only. Authentication not configured yet.');
  };

  const handleOtherLogin = () => {
    alert('Other login methods UI demo - not configured yet.');
  };

  return (
    <Container>
      {/* Main Card Container */}
      <MainCard>
        {/* Left Section - Welcome */}
        <LeftSection>
          {/* Geometric Decorations */}
          <GeometricSquare size="180px" top="-90px" left="-90px" opacity={0.1} />
          <GeometricSquare size="120px" top="30%" left="10%" opacity={0.08} />
          <GeometricSquare size="100px" top="60%" left="70%" opacity={0.06} />

          {/* 3D Sphere */}
          <Sphere />

          {/* Welcome Text */}
          <Box sx={{ position: 'relative', zIndex: 2 }}>
            <Typography
              variant="h2"
              sx={{
                fontWeight: 700,
                color: '#fff',
                mb: 2,
                fontSize: { xs: '2rem', md: '2.5rem' },
                letterSpacing: '1px'
              }}
            >
              WELCOME
            </Typography>
            <Typography
              variant="h6"
              sx={{
                color: 'rgba(255, 255, 255, 0.9)',
                fontWeight: 400,
                fontSize: { xs: '0.9rem', md: '1rem' },
                maxWidth: '300px'
              }}
            >
              YOUR HEADLINE NAME
            </Typography>
            <Typography
              variant="body2"
              sx={{
                color: 'rgba(255, 255, 255, 0.75)',
                mt: 2,
                fontSize: '0.85rem',
                lineHeight: 1.6,
                maxWidth: '280px'
              }}
            >
              Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            </Typography>
          </Box>
        </LeftSection>

        {/* Right Section - Sign In Form */}
        <RightSection>
          {/* Sign In Header */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 1, color: '#1a1a1a' }}>
            Sign In
          </Typography>
          <Typography variant="body2" sx={{ color: '#666', mb: 4 }}>
            Sign in to your account to continue
          </Typography>

          {/* Login Form */}
          <form onSubmit={handleSubmit}>
            <Stack spacing={2.5}>
              {/* Email Input */}
              <Box>
                <StyledTextField
                  fullWidth
                  type="email"
                  placeholder="User name"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Box
                          sx={{
                            width: '20px',
                            height: '20px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                            <path
                              d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z"
                              fill="#999"
                            />
                          </svg>
                        </Box>
                      </InputAdornment>
                    )
                  }}
                />
              </Box>

              {/* Password Input */}
              <Box>
                <StyledTextField
                  fullWidth
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Box
                          sx={{
                            width: '20px',
                            height: '20px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                            <path
                              d="M18 8H17V6C17 3.24 14.76 1 12 1C9.24 1 7 3.24 7 6V8H6C4.9 8 4 8.9 4 10V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V10C20 8.9 19.1 8 18 8ZM12 17C10.9 17 10 16.1 10 15C10 13.9 10.9 13 12 13C13.1 13 14 13.9 14 15C14 16.1 13.1 17 12 17ZM15 8H9V6C9 4.34 10.34 3 12 3C13.66 3 15 4.34 15 6V8Z"
                              fill="#999"
                            />
                          </svg>
                        </Box>
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton onClick={() => setShowPassword(!showPassword)} edge="end" size="small">
                          {showPassword ? <EyeInvisibleOutlined /> : <EyeOutlined />}
                        </IconButton>
                      </InputAdornment>
                    )
                  }}
                />
              </Box>

              {/* Remember Me & Forgot Password */}
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      size="small"
                      sx={{ color: '#2563c4', '&.Mui-checked': { color: '#2563c4' } }}
                    />
                  }
                  label={<Typography variant="body2">Remember me</Typography>}
                />
                <Link href="#" variant="body2" sx={{ color: '#2563c4', textDecoration: 'none', fontWeight: 500 }}>
                  Forgot
                </Link>
              </Box>

              {/* Sign In Button */}
              <SignInButton type="submit" fullWidth variant="contained">
                Sign In
              </SignInButton>

              {/* Sign in with other */}
              <OutlinedButton fullWidth variant="outlined" onClick={handleOtherLogin}>
                Sign in with other
              </OutlinedButton>
            </Stack>
          </form>
        </RightSection>
      </MainCard>
    </Container>
  );
}
