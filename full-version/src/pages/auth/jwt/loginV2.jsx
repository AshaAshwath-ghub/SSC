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
import Link from '@mui/material/Link';
import { styled } from '@mui/material/styles';

// icons
import EyeOutlined from '@ant-design/icons/EyeOutlined';
import EyeInvisibleOutlined from '@ant-design/icons/EyeInvisibleOutlined';

// ================================|| STYLED COMPONENTS ||================================ //

const Container = styled(Box)(({ theme }) => ({
  display: 'flex',
  height: '100vh',
  width: '100vw',
  overflow: 'hidden',
  position: 'relative',
  backgroundImage: 'url(https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=1920)',
  backgroundSize: 'cover',
  backgroundPosition: 'center',
  backgroundRepeat: 'no-repeat',
  '&::before': {
    content: '""',
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'linear-gradient(90deg, rgba(0, 0, 0, 0.05) 0%, rgba(0, 0, 0, 0.15) 100%)',
    zIndex: 1,
    pointerEvents: 'none'
  },
  [theme.breakpoints.down('md')]: {
    backgroundImage: 'none',
    background: '#f5f5f5'
  }
}));

const RightSection = styled(Box)(({ theme }) => ({
  position: 'relative',
  zIndex: 10,
  marginLeft: 'auto',
  width: '30%',
  minWidth: '400px',
  background: '#FFFFFF',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: '30px 40px',
  [theme.breakpoints.down('md')]: {
    width: '100%',
    minWidth: 'auto',
    padding: '40px 30px'
  },
  [theme.breakpoints.down('sm')]: {
    padding: '30px 20px'
  }
}));

const LoginContainer = styled(Box)({
  width: '100%',
  maxWidth: '380px'
});

const SocialButton = styled(Button)({
  width: '100%',
  padding: '10px',
  background: '#FFFFFF',
  color: '#5E5E5E',
  border: '1px solid #D5D5D5',
  borderRadius: '6px',
  fontSize: '13px',
  fontWeight: 500,
  textTransform: 'none',
  justifyContent: 'center',
  gap: '8px',
  transition: 'all 0.3s ease',
  '&:hover': {
    background: '#F5F5F5',
    borderColor: '#C0C0C0'
  }
});

const Footer = styled(Box)(({ theme }) => ({
  position: 'absolute',
  bottom: '20px',
  left: 0,
  right: 0,
  textAlign: 'center',
  fontSize: '12px',
  color: '#666666',
  [theme.breakpoints.down('md')]: {
    position: 'static',
    marginTop: '30px'
  }
}));

// ================================|| JWT - LOGIN V2 ||================================ //

export default function LoginV2() {
  const [showPassword, setShowPassword] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Login attempt (UI only):', { username, password: '***' });
    alert('This is UI demo only. Authentication not configured yet.');
  };

  const handleSocialLogin = (provider) => {
    alert(`${provider} login UI demo - not configured yet.`);
  };

  return (
    <Container>
      <RightSection>
        <LoginContainer>
          {/* Logo */}
          <Box sx={{ textAlign: 'center', mb: 3 }}>
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
          <Typography variant="h5" sx={{ fontWeight: 600, textAlign: 'center', mb: 3, mt: 2 }}>
            Sign in to your account
          </Typography>

          {/* Login Form */}
          <form onSubmit={handleSubmit}>
            <Stack spacing={2}>
              {/* Username Input */}
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 1, color: '#333', fontSize: '13px' }}>
                  Username
                </Typography>
                <TextField
                  fullWidth
                  type="text"
                  placeholder="Enter username or email"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  size="small"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: '6px'
                    }
                  }}
                />
              </Box>

              {/* Password Input */}
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="body2" sx={{ fontWeight: 600, color: '#333', fontSize: '13px' }}>
                    Password
                  </Typography>
                  <Link href="#" sx={{ fontSize: '12px', textDecoration: 'none' }}>
                    Report an issue
                  </Link>
                </Box>
                <TextField
                  fullWidth
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  size="small"
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton onClick={() => setShowPassword(!showPassword)} edge="end" size="small">
                          {showPassword ? <EyeInvisibleOutlined /> : <EyeOutlined />}
                        </IconButton>
                      </InputAdornment>
                    )
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
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
                sx={{
                  mt: 2,
                  py: 1.5,
                  fontSize: '14px',
                  fontWeight: 600,
                  textTransform: 'none',
                  borderRadius: '6px',
                  boxShadow: '0 2px 8px rgba(65, 105, 225, 0.3)',
                  '&:hover': {
                    boxShadow: '0 4px 12px rgba(65, 105, 225, 0.4)'
                  }
                }}
              >
                Sign in
              </Button>
            </Stack>
          </form>

          {/* Divider */}
          <Box sx={{ display: 'flex', alignItems: 'center', my: 2.5 }}>
            <Divider sx={{ flex: 1 }} />
            <Typography variant="caption" sx={{ px: 2, color: '#999' }}>
              OR
            </Typography>
            <Divider sx={{ flex: 1 }} />
          </Box>

          {/* Social Login Buttons */}
          <Stack spacing={1.25}>
            <SocialButton onClick={() => handleSocialLogin('Microsoft')}>
              <svg width="18" height="18" viewBox="0 0 23 23" fill="none">
                <path d="M0 0h10.933v10.933H0z" fill="#f25022" />
                <path d="M12.067 0H23v10.933H12.067z" fill="#00a4ef" />
                <path d="M0 12.067h10.933V23H0z" fill="#7fba00" />
                <path d="M12.067 12.067H23V23H12.067z" fill="#ffb900" />
              </svg>
              Sign in with Microsoft
            </SocialButton>

            <SocialButton onClick={() => handleSocialLogin('Google')}>
              <svg width="18" height="18" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
              </svg>
              Sign in with Google
            </SocialButton>

            <SocialButton onClick={() => handleSocialLogin('Apple')}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z" />
              </svg>
              Sign in with Apple
            </SocialButton>
          </Stack>
        </LoginContainer>

        {/* Footer */}
        <Footer>
          <Stack direction="row" spacing={2.5} sx={{ justifyContent: 'center', mb: 1 }}>
            <Link href="#" sx={{ color: 'primary.main', textDecoration: 'none', fontSize: '12px' }}>
              Terms of use
            </Link>
            <Link href="#" sx={{ color: 'primary.main', textDecoration: 'none', fontSize: '12px' }}>
              Privacy policy
            </Link>
          </Stack>
          <Typography variant="caption">&copy; 2025 Your Company. All rights reserved.</Typography>
        </Footer>
      </RightSection>
    </Container>
  );
}
