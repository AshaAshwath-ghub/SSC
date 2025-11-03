import PropTypes from 'prop-types';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

// material-ui
import useMediaQuery from '@mui/material/useMediaQuery';
import Button from '@mui/material/Button';
import CardMedia from '@mui/material/CardMedia';
import Stack from '@mui/material/Stack';
import Tooltip from '@mui/material/Tooltip';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';

// project imports
import { APP_AUTH, AuthProvider } from 'config';

// assets
import Jwt from 'assets/images/icons/jwt.svg';
import Google from 'assets/images/icons/google.svg';
import Microsoft from 'assets/images/icons/microsoft.svg';
import Apple from 'assets/images/icons/apple.svg';

// ==============================|| SOCIAL BUTTON ||============================== //

export default function LoginProvider({ currentLoginWith }) {
  const downSM = useMediaQuery((theme) => theme.breakpoints.down('sm'));
  const navigate = useNavigate();
  const [openAppleModal, setOpenAppleModal] = useState(false);

  const loginHandlers = {
    Jwt: () => navigate(APP_AUTH === AuthProvider.JWT ? '/login' : '/jwt/login?auth=jwt'),
    Google: () => {
      // Redirect to Google OAuth
      window.location.href = 'http://localhost:3010/api/v1/oauth/google/authorize';
    },
    Microsoft: () => {
      // Redirect to Microsoft OAuth
      window.location.href = 'http://localhost:3010/api/v1/oauth/microsoft/authorize';
    },
    Apple: () => {
      // Open modal instead of alert
      setOpenAppleModal(true);
    }
  };

  const buttonData = [
    { name: 'jwt', icon: Jwt, handler: loginHandlers.Jwt },
    { name: 'google', icon: Google, handler: loginHandlers.Google },
    { name: 'microsoft', icon: Microsoft, handler: loginHandlers.Microsoft },
    { name: 'apple', icon: Apple, handler: loginHandlers.Apple }
  ];

  const currentLoginExists = buttonData.some((button) => button.name === currentLoginWith);

  return (
    <>
      <Stack
        direction="row"
        sx={{
          gap: { xs: 1, sm: 2 },
          justifyContent: { xs: 'space-around', sm: 'space-between' },
          '& .MuiButton-startIcon': { mr: { xs: 0, sm: 1 }, ml: { xs: 0, sm: -0.5 } }
        }}
      >
        {buttonData
          .filter((button) => {
            if (currentLoginExists) {
              return button.name !== currentLoginWith;
            }
            return button.name !== APP_AUTH;
          })
          .map((button) => (
            <Tooltip title={button.name} key={button.name}>
              <Button
                sx={{ borderColor: 'grey.300', color: 'grey.900', '&:hover': { borderColor: 'primary.400', backgroundColor: 'primary.100' } }}
                variant="outlined"
                color="secondary"
                fullWidth
                startIcon={<CardMedia component="img" sx={{ width: 26 }} src={button.icon} alt={button.name} />}
                onClick={button.handler}
              >
                {!downSM && button.name}
              </Button>
            </Tooltip>
          ))}
      </Stack>

      {/* Apple Login Modal */}
      <Dialog
        open={openAppleModal}
        onClose={() => setOpenAppleModal(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CardMedia component="img" sx={{ width: 32, height: 32 }} src={Apple} alt="Apple" />
            <Typography variant="h4">Apple Login - Coming Soon</Typography>
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          <Stack spacing={2}>
            <Typography variant="body1">
              Apple Sign-In is currently under development.
            </Typography>
            <Box sx={{ bgcolor: 'warning.lighter', p: 2, borderRadius: 1 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                📝 Note:
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Apple Sign-In requires an Apple Developer account ($99/year) to configure the necessary credentials and services.
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              Please use <strong>Google</strong> or <strong>Microsoft</strong> to sign in for now.
            </Typography>
          </Stack>
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={() => setOpenAppleModal(false)} variant="contained" color="primary">
            Got It
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

LoginProvider.propTypes = { currentLoginWith: PropTypes.string };
