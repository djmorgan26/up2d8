
export enum Role {
  USER = 'user',
  MODEL = 'model',
  ERROR = 'error'
}

export interface GroundingChunk {
  web: {
    uri: string;
    title: string;
  };
}

export interface Message {
  id: string;
  role: Role;
  content: string;
  timestamp?: string;
  sources?: GroundingChunk[];
}

export interface BrowseCategoryTopic {
  name: string;
  imageUrl: string;
}

export interface BrowseCategory {
  title: string;
  topics: BrowseCategoryTopic[];
}
