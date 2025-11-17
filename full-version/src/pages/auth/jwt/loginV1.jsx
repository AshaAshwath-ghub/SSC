import { useState } from 'react';

// material-ui
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import InputAdornment from '@mui/material/InputAdornment';
import IconButton from '@mui/material/IconButton';
import Divider from '@mui/material/Divider';
import { styled } from '@mui/material/styles';

// icons
import EyeOutlined from '@ant-design/icons/EyeOutlined';
import EyeInvisibleOutlined from '@ant-design/icons/EyeInvisibleOutlined';

// ================================|| STYLED COMPONENTS ||================================ //

const BackgroundLayer = styled(Box)({
  position: 'fixed',
  top: 0,
  left: 0,
  width: '100vw',
  height: '100vh',
  backgroundImage: 'url(https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=1920)',
  backgroundSize: 'cover',
  backgroundPosition: 'center',
  backgroundRepeat: 'no-repeat',
  zIndex: 0
});

const GradientOverlay = styled(Box)({
  position: 'fixed',
  top: 0,
  left: 0,
  width: '100vw',
  height: '100vh',
  background: `linear-gradient(90deg,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.05) 20%,
    rgba(255, 255, 255, 0.2) 40%,
    rgba(255, 255, 255, 0.5) 55%,
    rgba(255, 255, 255, 0.8) 65%,
    rgba(255, 255, 255, 1) 70%,
    rgba(255, 255, 255, 1) 100%)`,
  zIndex: 1,
  pointerEvents: 'none'
});

const LoginPanel = styled(Box)(({ theme }) => ({
  position: 'fixed',
  top: 0,
  right: 0,
  width: '35%',
  minWidth: '500px',
  height: '100vh',
  background: 'transparent',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: '40px 50px',
  zIndex: 10,
  overflowY: 'auto',
  [theme.breakpoints.down('md')]: {
    width: '100%',
    minWidth: 'auto',
    padding: '30px 20px',
    background: '#f5f5f5'
  }
}));

const LoginContainer = styled(Box)(({ theme }) => ({
  width: '100%',
  maxWidth: '400px',
  background: 'rgba(255, 255, 255, 0.95)',
  padding: '40px 30px',
  borderRadius: '12px',
  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
  [theme.breakpoints.down('sm')]: {
    padding: '30px 20px'
  }
}));

// ================================|| JWT - LOGIN V1 ||================================ //

export default function LoginV1() {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Login attempt (UI only):', { email, password: '***' });
    alert('This is UI demo only. Authentication not configured yet.');
  };

  const handleMicrosoftLogin = () => {
    alert('Microsoft login UI demo - not configured yet.');
  };

  return (
    <Box sx={{ height: '100vh', width: '100vw', overflow: 'hidden', position: 'relative' }}>
      {/* Background */}
      <BackgroundLayer />

      {/* Gradient Overlay */}
      <GradientOverlay />

      {/* Login Panel */}
      <LoginPanel>
        <LoginContainer>
          {/* Logo */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <svg width="140" height="35" viewBox="0 0 140 35" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="2" y="2" width="31" height="31" rx="7" fill="#1890FF" />
              <rect x="2" y="2" width="31" height="31" rx="7" stroke="#096DD9" strokeWidth="2" />
              <path d="M17.5 10L12 17.5H15.5V25L19.5 25V17.5H23L17.5 10Z" fill="#FFFFFF" />
              <text x="40" y="23" fontFamily="system-ui, -apple-system, sans-serif" fontSize="18" fontWeight="600" fill="#1a1a1a" fillOpacity="0.85">
                My App
              </text>
            </svg>
          </Box>

          {/* Heading */}
          <Typography variant="h4" sx={{ fontWeight: 600, textAlign: 'center', mb: 1 }}>
            Sign In
          </Typography>

          {/* Login Form */}
          <form onSubmit={handleSubmit}>
            <Stack spacing={2.5} sx={{ mt: 3 }}>
              {/* Email Input */}
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 1, color: '#333' }}>
                  Email <span style={{ color: '#000' }}>*</span>
                </Typography>
                <TextField
                  fullWidth
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      background: 'rgba(255, 255, 255, 0.9)',
                      borderRadius: '6px'
                    }
                  }}
                />
              </Box>

              {/* Password Input */}
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 1, color: '#333' }}>
                  Password <span style={{ color: '#000' }}>*</span>
                </Typography>
                <TextField
                  fullWidth
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          edge="end"
                          size="small"
                        >
                          {showPassword ? <EyeInvisibleOutlined /> : <EyeOutlined />}
                        </IconButton>
                      </InputAdornment>
                    )
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      background: 'rgba(255, 255, 255, 0.9)',
                      borderRadius: '6px'
                    }
                  }}
                />
              </Box>

              {/* Sign In Button */}
              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                sx={{
                  mt: 1,
                  py: 1.75,
                  fontSize: '15px',
                  fontWeight: 600,
                  textTransform: 'none',
                  borderRadius: '6px',
                  boxShadow: '0 2px 8px rgba(65, 105, 225, 0.3)',
                  '&:hover': {
                    boxShadow: '0 4px 12px rgba(65, 105, 225, 0.4)'
                  }
                }}
              >
                Sign In
              </Button>
            </Stack>
          </form>

          {/* Divider */}
          <Box sx={{ display: 'flex', alignItems: 'center', my: 3 }}>
            <Divider sx={{ flex: 1 }} />
            <Typography variant="body2" sx={{ px: 2, color: '#999' }}>
              OR
            </Typography>
            <Divider sx={{ flex: 1 }} />
          </Box>

          {/* Microsoft Button */}
          <Button
            fullWidth
            variant="outlined"
            onClick={handleMicrosoftLogin}
            sx={{
              py: 1.5,
              fontSize: '14px',
              fontWeight: 500,
              textTransform: 'none',
              borderRadius: '6px',
              color: '#5E5E5E',
              borderColor: '#D5D5D5',
              background: 'rgba(255, 255, 255, 0.9)',
              '&:hover': {
                background: '#F5F5F5',
                borderColor: '#C0C0C0'
              }
            }}
            startIcon={
              <svg width="20" height="20" viewBox="0 0 23 23" fill="none">
                <path d="M0 0h10.933v10.933H0z" fill="#f25022" />
                <path d="M12.067 0H23v10.933H12.067z" fill="#00a4ef" />
                <path d="M0 12.067h10.933V23H0z" fill="#7fba00" />
                <path d="M12.067 12.067H23V23H12.067z" fill="#ffb900" />
              </svg>
            }
          >
            Continue with Microsoft
          </Button>

          {/* Support Text */}
          <Typography variant="caption" sx={{ textAlign: 'center', color: '#666', mt: 4, display: 'block', lineHeight: 1.6 }}>
            Experiencing access issues or require assistance?<br />
            Please contact{' '}
            <Typography component="a" href="mailto:support@test.com" sx={{ color: 'primary.main', textDecoration: 'none' }}>
              support@test.com
            </Typography>
          </Typography>
        </LoginContainer>
      </LoginPanel>
    </Box>
  );
}
