// src/components/StreamingText.tsx
import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';

interface StreamingTextProps {
  text: string;
  speed?: number;
}

const StreamingText = ({ text, speed = 30 }: StreamingTextProps) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    let currentIndex = 0;
    setDisplayedText('');
    setIsComplete(false);

    const interval = setInterval(() => {
      if (currentIndex < text.length) {
        setDisplayedText((prev) => prev + text[currentIndex]);
        currentIndex++;
      } else {
        setIsComplete(true);
        clearInterval(interval);
      }
    }, speed);

    return () => clearInterval(interval);
  }, [text, speed]);

  return (
    <div className="prose max-w-none">
      <ReactMarkdown>
        {isComplete ? text : displayedText + '▋'}
      </ReactMarkdown>
    </div>
  );
};

export default StreamingText;