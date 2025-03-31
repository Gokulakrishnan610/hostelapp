import React, { useEffect, useState } from 'react';
import { 
  Container, Typography, Paper, Box, Button, FormControl, InputLabel, 
  MenuItem, Select, Chip, Dialog, DialogTitle, DialogContent, DialogActions, 
  Alert, CircularProgress, TextField, Stepper, Step, StepLabel, Divider
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { getRooms, makePayment, requestOtp, verifyOtp } from '../services/api';
import { getProfile } from '../services/api';
import { StyledGrid } from './common/StyledGrid';
import { ApiError } from '../types/api';
import { SelectChangeEvent } from '@mui/material/Select';
import Navbar from './common/Navbar';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { Carousel } from 'react-responsive-carousel';
import 'react-responsive-carousel/lib/styles/carousel.min.css';

interface RoomPhoto {
  id: number;
  title: string;
  description: string | null;
  image: string;
  is_primary: boolean;
}

interface Room {
  id: number;
  category: string;
  location: string;
  available_seats: number;
  menu: string;
  pax_per_room: number;
  price: number;
  gender: string;
  photos: RoomPhoto[];
  primary_photo: RoomPhoto | null;
}

const RoomSelection: React.FC = () => {
  // State for room selection and filtering
  const [rooms, setRooms] = useState<Room[]>([]);
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    menu: '',
    capacity: ''
  });
  const [selectedRoom, setSelectedRoom] = useState<Room | null>(null);
  
  // State for booking flow
  const [activeStep, setActiveStep] = useState(0);
  const [bookingDialogOpen, setBookingDialogOpen] = useState(false);
  const [paymentAmount, setPaymentAmount] = useState(0);
  const [transactionId, setTransactionId] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [otp, setOtp] = useState('');
  const [otpVerified, setOtpVerified] = useState(false);
  const [bookingConfirmed, setBookingConfirmed] = useState(false);
  
  const navigate = useNavigate();
  
  const fetchRooms = async () => {
    try {
      setLoading(true);
      // Get profile first
      const profileRes = await getProfile();
      setProfile(profileRes.data);

      // Make API request for rooms
      const roomsRes = await getRooms({
        gender: profileRes.data.gender,
        menu: filters.menu,
        capacity: filters.capacity
      });
      
      console.log("API Response:", roomsRes.data);
      setRooms(roomsRes.data);
      
    } catch (error) {
      console.error("Error fetching rooms:", error);
      toast.error("Failed to load rooms. Please try again.");
      setError("Failed to load rooms. Please try again later.");
    } finally {
      setLoading(false);
    }
  };
  
  // Fetch rooms on initial load and when filters change
  useEffect(() => {
    fetchRooms();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);
  
  const handleFilterChange = (event: SelectChangeEvent<string>) => {
    const { name, value } = event.target;
    if (name) {
      setFilters(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };
  
  const handleRoomSelect = (room: Room) => {
    setSelectedRoom(room);
    
    // Calculate payment amount based on room type
    const baseAmount = 10000;
    let multiplier = 1;
    
    if (room.category.includes('AC')) {
      multiplier = 1.5;
    }
    
    const capacity = room.pax_per_room;
    if (capacity <= 2) {
      multiplier *= 1.2;
    } else if (capacity <= 4) {
      multiplier *= 1;
    } else {
      multiplier *= 0.8;
    }
    
    setPaymentAmount(Math.round(baseAmount * multiplier));
    setActiveStep(0);
    setBookingDialogOpen(true);
  };
  
  const handleSendOtp = async () => {
    if (!profile?.email) {
      toast.error("Email not found in your profile");
      return;
    }
    
    try {
      setLoading(true);
      
      // Call the requestOtp API - no need to pass email, it will use the authenticated user
      await requestOtp();
      
      setOtpSent(true);
      toast.success(`OTP sent to ${profile.email}`);
      setActiveStep(1);
    } catch (error) {
      console.error("Error sending OTP:", error);
      toast.error("Failed to send OTP. Please try again.");
    } finally {
      setLoading(false);
    }
  };
  
  const handleVerifyOtp = async () => {
    if (!otp) {
      toast.error("Please enter the OTP");
      return;
    }
    
    try {
      setLoading(true);
      
      // Call the verifyOtp API with just the OTP
      await verifyOtp(otp);
      
      setOtpVerified(true);
      toast.success("OTP verified successfully");
      setActiveStep(2);
    } catch (error) {
      console.error("Error verifying OTP:", error);
      toast.error("Invalid OTP. Please check and try again.");
    } finally {
      setLoading(false);
    }
  };
  
  const handlePaymentSubmit = async () => {
    if (!transactionId) {
      toast.error("Please enter a transaction ID");
      return;
    }
    
    try {
      setLoading(true);
      
      if (!selectedRoom) {
        throw new Error("No room selected");
      }
      
      // Call the makePayment API
      await makePayment({
        room_id: selectedRoom.id,
        amount: paymentAmount,
        transaction_id: transactionId
      });
      
      setBookingConfirmed(true);
      toast.success("Room booking request submitted successfully");
      setActiveStep(3);
      
      // Refresh room data after 2 seconds
      setTimeout(() => {
        fetchRooms();
      }, 2000);
      
    } catch (error) {
      console.error("Error submitting payment:", error);
      toast.error("Failed to submit payment. Please try again.");
    } finally {
      setLoading(false);
    }
  };
  
  const handleCloseDialog = () => {
    setBookingDialogOpen(false);
    setOtp('');
    setOtpSent(false);
    setOtpVerified(false);
    setTransactionId('');
    setBookingConfirmed(false);
    setSelectedRoom(null);
  };
  
  const renderBookingStepContent = () => {
    switch (activeStep) {
      case 0:
        return (
          <>
            <Typography variant="h6" gutterBottom>
              Room Details
            </Typography>
            
            <Box sx={{ my: 2 }}>
              <Typography variant="body1" gutterBottom>
                <strong>Category:</strong> {selectedRoom?.category}
              </Typography>
              <Typography variant="body1" gutterBottom>
                <strong>Location:</strong> {selectedRoom?.location}
              </Typography>
              <Typography variant="body1" gutterBottom>
                <strong>Capacity:</strong> {selectedRoom?.pax_per_room} persons
              </Typography>
              <Typography variant="body1" gutterBottom>
                <strong>Menu:</strong> {selectedRoom?.menu}
              </Typography>
            </Box>
            
            <Divider sx={{ my: 2 }} />
            
            <Typography variant="body1" gutterBottom>
              <strong>Amount to Pay:</strong>{' '}
              <Typography component="span" variant="h6" color="primary">
                ₹{selectedRoom?.price.toLocaleString()}
              </Typography>
            </Typography>
            
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              To continue with booking, we'll send an OTP to your email ({profile?.email}) for verification.
            </Typography>
            
            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
              <Button 
                variant="contained" 
                onClick={handleSendOtp}
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} /> : "Send OTP"}
              </Button>
            </Box>
          </>
        );
        
      case 1:
        return (
          <>
            <Typography variant="h6" gutterBottom>
              Verify OTP
            </Typography>
            
            <Typography variant="body2" gutterBottom sx={{ mb: 2 }}>
              An OTP has been sent to your email address ({profile?.email}).
            </Typography>
            
            <TextField
              label="Enter OTP"
              variant="outlined"
              fullWidth
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              sx={{ mb: 3 }}
            />
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Button onClick={() => handleSendOtp()}>
                Resend OTP
              </Button>
              <Button 
                variant="contained" 
                onClick={handleVerifyOtp}
                disabled={loading || !otp}
              >
                {loading ? <CircularProgress size={24} /> : "Verify OTP"}
              </Button>
            </Box>
          </>
        );
        
      case 2:
        return (
          <>
            <Typography variant="h6" gutterBottom>
              Payment Information
            </Typography>
            
            <Typography variant="body2" gutterBottom sx={{ mb: 3 }}>
              Please make a payment of <strong>₹{selectedRoom?.price.toLocaleString()}</strong> via UPI/Net Banking/Card.
            </Typography>
            
            <Typography variant="body2" gutterBottom>
              After payment, enter the transaction ID below:
            </Typography>
            
            <TextField
              label="Transaction ID"
              variant="outlined"
              fullWidth
              value={transactionId}
              onChange={(e) => setTransactionId(e.target.value)}
              sx={{ my: 3 }}
            />
            
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 3 }}>
              Note: This is a simulated payment flow. In a real application, you would be redirected to a payment gateway.
            </Typography>
            
            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button 
                variant="contained" 
                onClick={handlePaymentSubmit}
                disabled={loading || !transactionId}
              >
                {loading ? <CircularProgress size={24} /> : "Submit Payment"}
              </Button>
            </Box>
          </>
        );
        
      case 3:
        return (
          <>
            <Box sx={{ textAlign: 'center', my: 3 }}>
              <Typography variant="h6" gutterBottom color="primary">
                Booking Submitted Successfully!
              </Typography>
              
              <Typography variant="body1" gutterBottom sx={{ mt: 2 }}>
                Your room booking request has been submitted for admin verification.
              </Typography>
              
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                You can view the status of your booking on the dashboard.
              </Typography>
              
              <Box sx={{ mt: 3 }}>
                <Button 
                  variant="outlined" 
                  onClick={() => navigate('/dashboard')}
                  sx={{ mr: 2 }}
                >
                  Go to Dashboard
                </Button>
                <Button 
                  variant="contained" 
                  onClick={handleCloseDialog}
                >
                  Close
                </Button>
              </Box>
            </Box>
          </>
        );
        
      default:
        return <Typography>Unknown step</Typography>;
    }
  };

  return (
    <>
      <Navbar />
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <ToastContainer position="top-right" autoClose={5000} />
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" gutterBottom>
            Room Selection
          </Typography>
          <Typography color="textSecondary">
            Showing rooms for {profile?.gender || '...'} students
          </Typography>
        </Box>
        
        {/* Filters */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <StyledGrid container spacing={2} alignItems="center">
            <StyledGrid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Menu Preference</InputLabel>
                <Select
                  name="menu"
                  value={filters.menu}
                  label="Menu Preference"
                  onChange={handleFilterChange}
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="Veg">Vegetarian</MenuItem>
                  <MenuItem value="Non Veg">Non-Vegetarian</MenuItem>
                </Select>
              </FormControl>
            </StyledGrid>
            <StyledGrid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Room Capacity</InputLabel>
                <Select
                  name="capacity"
                  value={filters.capacity}
                  label="Room Capacity"
                  onChange={handleFilterChange}
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="1">Single</MenuItem>
                  <MenuItem value="2">Double</MenuItem>
                  <MenuItem value="3">Triple</MenuItem>
                  <MenuItem value="4">Four-Person</MenuItem>
                  <MenuItem value="5">Five-Person</MenuItem>
                  <MenuItem value="6">Six-Person</MenuItem>
                </Select>
              </FormControl>
            </StyledGrid>
          </StyledGrid>
        </Paper>
        
        {/* Room display */}
        {loading && !bookingDialogOpen ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <StyledGrid container spacing={3}>
            {rooms && rooms.length > 0 ? (
              rooms.map((room) => (
                <StyledGrid key={room.id} item xs={12} sm={6} md={4}>
                  <Paper 
                    sx={{ 
                      p: 0, 
                      height: '100%', 
                      display: 'flex', 
                      flexDirection: 'column',
                      transition: 'transform 0.2s',
                      overflow: 'hidden',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: 3
                      }
                    }}
                  >
                    {/* Room Images */}
                    {room.photos && room.photos.length > 0 ? (
                      <Box sx={{ width: '100%', height: 200, position: 'relative' }}>
                        <Carousel 
                          showArrows={true}
                          showStatus={false}
                          showThumbs={false}
                          infiniteLoop={true}
                          autoPlay={false}
                          swipeable={true}
                          emulateTouch={true}
                        >
                          {room.photos.map((photo) => (
                            <Box key={photo.id} sx={{ height: 200 }}>
                              <img 
                                src={photo.image} 
                                alt={photo.title}
                                style={{ 
                                  width: '100%', 
                                  height: '200px', 
                                  objectFit: 'cover' 
                                }}
                              />
                            </Box>
                          ))}
                        </Carousel>
                      </Box>
                    ) : (
                      room.primary_photo ? (
                        <Box sx={{ width: '100%', height: 200, position: 'relative' }}>
                          <img 
                            src={room.primary_photo.image} 
                            alt={room.primary_photo.title}
                            style={{ 
                              width: '100%', 
                              height: '200px', 
                              objectFit: 'cover' 
                            }}
                          />
                        </Box>
                      ) : (
                        <Box 
                          sx={{ 
                            width: '100%', 
                            height: 200, 
                            bgcolor: 'grey.200', 
                            display: 'flex', 
                            alignItems: 'center', 
                            justifyContent: 'center'
                          }}
                        >
                          <Typography variant="body2" color="text.secondary">
                            No photo available
                          </Typography>
                        </Box>
                      )
                    )}

                    {/* Room Details */}
                    <Box sx={{ p: 3, flex: 1, display: 'flex', flexDirection: 'column' }}>
                      <Typography variant="h6" gutterBottom color="primary">
                        {room.category}
                      </Typography>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body1">
                          <strong>Location:</strong> {room.location}
                        </Typography>
                        <Typography variant="body1">
                          <strong>Menu:</strong> {room.menu}
                        </Typography>
                        <Typography variant="body1">
                          <strong>For:</strong> {room.gender || profile?.gender} students
                        </Typography>
                        <Typography variant="body1">
                          <strong>Capacity:</strong> {room.pax_per_room} persons
                        </Typography>
                        <Typography variant="body1" sx={{ fontWeight: 'bold', color: 'primary.main', mt: 1 }}>
                          <strong>Price:</strong> ₹{room.price.toLocaleString()}
                        </Typography>
                        <Typography variant="body1" sx={{ mt: 1 }}>
                          <strong>Available Seats:</strong>{' '}
                          <Chip 
                            label={room.available_seats} 
                            color={room.available_seats > 0 ? 'success' : 'error'}
                            size="small"
                          />
                        </Typography>
                      </Box>
                      <Button 
                        variant="contained" 
                        fullWidth 
                        sx={{ mt: 2 }}
                        disabled={room.available_seats <= 0 || !!profile?.room}
                        onClick={() => handleRoomSelect(room)}
                      >
                        {profile?.room ? 'Already Booked' : 'Select Room'}
                      </Button>
                    </Box>
                  </Paper>
                </StyledGrid>
              ))
            ) : (
              <StyledGrid item xs={12}>
                <Paper sx={{ p: 3, textAlign: 'center' }}>
                  <Typography variant="h6" color="textSecondary" gutterBottom>
                    No rooms available matching your criteria.
                  </Typography>
                  <Typography color="textSecondary" paragraph>
                    The system is set up to show only {profile?.gender} hostel rooms for you.
                  </Typography>
                  <Button 
                    variant="outlined" 
                    sx={{ mt: 2 }} 
                    onClick={() => setFilters({ menu: '', capacity: '' })}
                  >
                    Reset Filters
                  </Button>
                </Paper>
              </StyledGrid>
            )}
          </StyledGrid>
        )}
        
        {/* Booking Dialog with Steps */}
        <Dialog 
          open={bookingDialogOpen} 
          onClose={handleCloseDialog}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle sx={{ borderBottom: '1px solid #eee', pb: 2 }}>
            Room Booking
          </DialogTitle>
          
          <DialogContent sx={{ pt: 3, pb: 1 }}>
            <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
              <Step>
                <StepLabel>Room Details</StepLabel>
              </Step>
              <Step>
                <StepLabel>Verify Email</StepLabel>
              </Step>
              <Step>
                <StepLabel>Payment</StepLabel>
              </Step>
              <Step>
                <StepLabel>Confirmation</StepLabel>
              </Step>
            </Stepper>
            
            {renderBookingStepContent()}
          </DialogContent>
          
          {activeStep < 3 && (
            <DialogActions sx={{ borderTop: '1px solid #eee', pt: 2 }}>
              <Button onClick={handleCloseDialog}>Cancel</Button>
            </DialogActions>
          )}
        </Dialog>
      </Container>
    </>
  );
};

export default RoomSelection; 