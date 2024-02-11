import React, { useState, useEffect, useMemo } from "react";
import {
  Text,
  Space,
  Box,
  Group,
  Loader,
  Center,
  Skeleton,
  Divider,
} from "@mantine/core";
import { IconArrowRight } from "@tabler/icons-react";
import {
  ComposableMap,
  Geographies,
  Geography,
  ZoomableGroup,
  Line,
  Marker,
} from "react-simple-maps";
import { API_BASE, STATIC_BASE, secondsFormat, kgFormat, dateFormat } from "../helpers";

const getWaypointCoords = (flight: any) => {
  return flight["waypoints"].map((waypoint: []) => [
    waypoint["lon"],
    waypoint["lat"],
  ]);
};

const middlePointAndDir = (coords: []) => {
  const middle = Math.floor(coords.length / 2);
  const leftPoint = coords[middle - 1];
  const middlePoint = coords[middle];
  const rightPoint = coords[middle + 1];
  const dir = Math.atan2(
    rightPoint[1] - leftPoint[1],
    rightPoint[0] - leftPoint[0]
  );
  return [middlePoint, dir];
};

const getCenterZoom = (coords: []) => {
  const minLat = Math.min(...coords.map((coord) => coord[1]));
  const maxLat = Math.max(...coords.map((coord) => coord[1]));
  const minLon = Math.min(...coords.map((coord) => coord[0]));
  const maxLon = Math.max(...coords.map((coord) => coord[0]));
  const latDiff = Math.abs(maxLat - minLat);
  const lonDiff = Math.abs(maxLon - minLon);
  const zoom = Math.min(100 / latDiff, 100 / lonDiff) * 0.85;
  const center = [(minLon + maxLon) / 2, (minLat + maxLat) / 2];
  const weight = zoom / 250;
  return [center, zoom, weight];
};

const getMetrics = (flightDetails: any) => {
  return [
    {
      label: <>CO<sub>2</sub> eq</>,
      value: kgFormat(flightDetails["emissions_kg"]),
    },
    // {
    //   label: "Fuel Burned",
    //   value: kgFormat(flightDetails["fuel_used_kg"]),
    // },
    {
      label: "Distance",
      value: flightDetails["distance_km"].toFixed(0) + " km",
    },
    {
      label: "Duration",
      value: secondsFormat(flightDetails["duration_s"]),
    }
  ];
}

export const EmissionsCard = ({ entry }: any) => {
  const [flightDetails, setFlightDetails] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/get_flight/${entry["id"]}`)
      .then((response) => response.json())
      .then(setFlightDetails);
  }, [entry]); // Dependency array to ensure effect runs only when id changes

  const waypointCoords = useMemo(
    () => (flightDetails ? getWaypointCoords(flightDetails) : []),
    [flightDetails]
  );
  const [center, zoom, weight] = useMemo(
    () =>
      waypointCoords.length > 0 ? getCenterZoom(waypointCoords) : [[0, 0], 1, 1],
    [waypointCoords]
  );
  const [middlePoint, dir] = useMemo(
    () =>
      waypointCoords.length > 0
        ? middlePointAndDir(waypointCoords)
        : [[0, 0], 0],
    [waypointCoords]
  );
  const metrics = useMemo(
    () =>
      flightDetails
        ? getMetrics(flightDetails)
        : []
  , [flightDetails]
  );

  return (
    <Box w={300}>
      <Group justify="space-between">
        <Text size="lg">
          {entry.starting_airport} <IconArrowRight size="0.75em"/>{" "}
          {entry.ending_airport}
        </Text>
        <Text size="lg">{dateFormat(entry.starting_time)}</Text>
      </Group>
      <Space h={10} />
      {flightDetails ? (
        <>
          <ComposableMap width={300} height={200}>
            <ZoomableGroup center={center} zoom={zoom} maxZoom={200}>
              <Geographies
                geography={STATIC_BASE + "/static/worldMapFeatures.json"}
              >
                {({ geographies }: any) =>
                  geographies.map((geo: any) => (
                    <Geography
                      key={geo.rsmKey}
                      geography={geo}
                      fill="#EAEAEC"
                      stroke="#D6D6DA"
                      strokeWidth={0.07}
                    />
                  ))
                }
              </Geographies>
              <Line
                coordinates={waypointCoords}
                stroke="#FFC078"
                strokeWidth={weight}
              />
              {waypointCoords.slice(1, -1).map((coord: any) => (
                <Marker coordinates={coord} key={coord}>
                  <circle r={weight} fill="#FFC078" />
                </Marker>
              ))}
              <Marker coordinates={waypointCoords[0]}>
                <circle r={weight*2} fill="#fd7e14" stroke="#EAEAEC" strokeWidth={weight / 1.5} />
              </Marker>
              <Marker coordinates={waypointCoords[waypointCoords.length - 1]}>
                <circle r={weight*2} fill="#fd7e14" stroke="#EAEAEC" strokeWidth={weight / 1.5} />
              </Marker>
              <Marker coordinates={middlePoint}>
                {/* <path stroke="none" d="M0 0h24v24H0z" fill="none"/> */}
                <path
                  d="M16 10h4a2 2 0 0 1 0 4h-4l-4 7h-3l2 -7h-4l-2 2h-3l2 -4l-2 -4h3l2 2h4l-2 -7h3z"
                  fill="#fd7e14"
                  stroke="#EAEAEC"
                  strokeWidth={weight * 30}
                  transform={`scale(${weight / 2}) translate(-12 -12) rotate(${
                    (-dir * 180) / Math.PI
                  } 12 12)`}
                />
                <path
                  d="M16 10h4a2 2 0 0 1 0 4h-4l-4 7h-3l2 -7h-4l-2 2h-3l2 -4l-2 -4h3l2 2h4l-2 -7h3z"
                  fill="#fd7e14"
                  transform={`scale(${weight / 2}) translate(-12 -12) rotate(${
                    (-dir * 180) / Math.PI
                  } 12 12)`}
                />
              </Marker>
            </ZoomableGroup>
          </ComposableMap>
          <Group mt={20} justify="space-between">
            {metrics && metrics.map((metric: any) => (
              <>
              <Box key={metric["label"]} flex={1}>
                <Center>
                <Text size="xs" c="gray.7">
                  {metric["label"]}
                </Text>
                </Center>
                <Center>
                <Text size="md" c="orange.6" fw="bold" ff="IBM Plex Mono">{metric["value"]}</Text>
                </Center>
              </Box>
              { metric !== metrics[metrics.length - 1] &&
              <Divider orientation="vertical" />
              }
              </>
            ))}
            </Group>
        </>
      ) : (
        <Skeleton height={200} width={300} />
      )}
    </Box>
  );
};
