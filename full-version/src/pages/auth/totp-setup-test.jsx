import { Box, Container, Typography } from '@mui/material';
import AuthTOTPSetup from 'sections/auth/jwt/AuthTOTPSetup';
import { useNavigate } from 'react-router-dom';

/**
 * Standalone TOTP Setup Test Page
 *
 * This is a test page to set up TOTP for a user.
 * In production, this would be part of the user profile settings.
 */
const TOTPSetupTest = () => {
  const navigate = useNavigate();

  const handleSetupComplete = (data) => {
    console.log('TOTP setup completed:', data);
    alert('TOTP setup successful! You can now use it during login.');
    // Navigate to login page
    navigate('/login');
  };

  const handleCancel = () => {
    navigate('/login');
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8, mb: 4 }}>
        <Typography variant="h2" gutterBottom align="center">
          TOTP Setup Test
        </Typography>
        <Typography variant="body1" color="text.secondary" align="center" sx={{ mb: 4 }}>
          Set up your authenticator app for testing
        </Typography>

        {/* TOTP Setup for user: niteesh.kl@jillellagroup.com */}
        <AuthTOTPSetup
          userEmail="jayendhar.murali@jillellagroup.com"
          onSetupComplete={handleSetupComplete}
          onCancel={handleCancel}
        />
      </Box>
    </Container>
  );
};

export default TOTPSetupTest;
