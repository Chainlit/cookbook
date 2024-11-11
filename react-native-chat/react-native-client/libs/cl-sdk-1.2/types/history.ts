import { IThread } from 'cl-sdk-1.2/types';

import { IPageInfo } from '..';

export type UserInput = {
  content: string;
  createdAt: number;
};

export type ThreadHistory = {
  threads?: IThread[];
  currentThreadId?: string;
  timeGroupedThreads?: { [key: string]: IThread[] };
  pageInfo?: IPageInfo;
};
