import PropTypes from 'prop-types';
import { useNavigate } from 'react-router-dom';

// material-ui
import useMediaQuery from '@mui/material/useMediaQuery';
import Button from '@mui/material/Button';
import CardMedia from '@mui/material/CardMedia';
import Stack from '@mui/material/Stack';
import Tooltip from '@mui/material/Tooltip';

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
      // Apple OAuth requires Apple Developer account
      alert('Apple Login - Coming Soon\n\nApple Sign-In is currently under development.\n\nNote: Apple Sign-In requires an Apple Developer account ($99/year) to configure the necessary credentials and services.\n\nPlease use Google or Microsoft to sign in.');
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
  );
}

LoginProvider.propTypes = { currentLoginWith: PropTypes.string };
