import React from 'react';
import {Composition} from 'remotion';
import {Banner, FPS, DURATION} from './Banner';
export const Root: React.FC = () => (
  <Composition id="Banner" component={Banner} durationInFrames={DURATION} fps={FPS} width={1200} height={300} />
);
