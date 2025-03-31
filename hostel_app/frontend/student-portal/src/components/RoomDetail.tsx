import React from 'react';
import { Box, Typography } from '@mui/material';
import { Carousel } from 'react-responsive-carousel';
import 'react-responsive-carousel/lib/styles/carousel.min.css';

// Define an interface for photo
interface Photo {
  id: number;
  title: string;
  description?: string;
  image: string;
  is_primary: boolean;
}

// Define an interface for room
interface RoomProps {
  id: number;
  category: string;
  location: string;
  menu: string;
  pax_per_room: number;
  available_seats: number;
  photos: Photo[];
  primary_photo?: Photo | null;
  gender?: string;
  created_at: string;
  updated_at: string;
}

// Define props for the component
interface RoomDetailProps {
  room: RoomProps;
}

const RoomDetail: React.FC<RoomDetailProps> = ({ room }) => {
  return (
    <Box sx={{ mb: 4 }}>
      {room.photos && room.photos.length > 0 ? (
        <Carousel 
          showArrows={true}
          showStatus={false}
          showThumbs={true}
          infiniteLoop={true}
        >
          {room.photos.map((photo: Photo) => (
            <div key={photo.id}>
              <img 
                src={photo.image} 
                alt={photo.title}
                style={{ maxHeight: '400px', objectFit: 'cover' }}
              />
              <p className="legend">{photo.title}</p>
            </div>
          ))}
        </Carousel>
      ) : (
        <Box sx={{ height: 300, backgroundColor: 'grey.200', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <Typography variant="body1" color="textSecondary">No photos available</Typography>
        </Box>
      )}
    </Box>
  );
};

export default RoomDetail; 