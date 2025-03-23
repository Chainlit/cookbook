import React, { useEffect, useRef } from "react";
import { useRecoilValue } from "recoil";
import { callFnState } from "@chainlit/react-client";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";

export default function GoogleMap() {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const callFn = useRecoilValue(callFnState);

  useEffect(() => {
    // Check if API is already loaded
    if (window.google && window.google.maps) {
      // Maps API already loaded, initialize map directly
      initializeMap();
      return;
    }

    // Check if the script is already in the process of loading
    const existingScript = document.querySelector(
      `script[src^="https://maps.googleapis.com/maps/api/js"]`
    );

    if (existingScript) {
      // Script is loading but not ready, wait for it
      const originalCallback = window.initMap;
      window.initMap = () => {
        if (originalCallback) originalCallback();
        initializeMap();
      };
      return;
    }

    // Load the script only if it's not already loaded or loading
    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?&callback=initMap`;
    script.async = true;
    script.defer = true;

    // Define the callback function
    window.initMap = initializeMap;

    document.head.appendChild(script);

    // Clean up
    return () => {
      // Don't remove the script as other components might be using it
      // Just clean up our callback
      if (window.initMap === initializeMap) {
        window.initMap = null;
      }
    };
  }, []);

  useEffect(() => {
    if (callFn?.name === "move-map") {
      const { latitude, longitude } = callFn.args;
      moveMapTo(latitude, longitude);
      callFn.callback();
    }
  }, [callFn]);

  const initializeMap = () => {
    if (mapRef.current && !mapInstanceRef.current) {
      mapInstanceRef.current = new window.google.maps.Map(mapRef.current, {
        center: { lat: props.latitude, lng: props.longitude },
        zoom: props.zoom,
      });
    }
  };

  const moveMapTo = (newLat, newLng, newZoom = 12) => {
    if (!mapInstanceRef.current) return false;

    // Create a new LatLng object
    const newPosition = new window.google.maps.LatLng(newLat, newLng);

    // Pan the map to the new position
    mapInstanceRef.current.panTo(newPosition);

    // Update zoom if provided
    if (newZoom !== null) {
      mapInstanceRef.current.setZoom(newZoom);
    }

    return true;
  };

  return (
    <div className="h-full w-full relative">
      <Button
        className="absolute z-10"
        style={{top: ".5rem", left: ".5rem"}}
        onClick={() => callAction({ name: "close_map", payload: {} })}
        size="icon"
      >
        <ArrowLeft />
      </Button>
      <div ref={mapRef} className="h-full w-full" />
    </div>
  );
}
