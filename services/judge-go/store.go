package main

import (
	"context"
	"fmt"
	"io"
	"os"
	"strings"
	"sync"

	"github.com/minio/minio-go/v7"
	"github.com/minio/minio-go/v7/pkg/credentials"
)

// Test ma'lumoti DB da emas, S3 da (08-technical-spec: judge → S3 ✅,
// judge → API/DB ❌). Worker faqat `s3://bucket/key` havolasini oladi.
type store struct {
	client        *minio.Client
	defaultBucket string

	mu    sync.Mutex
	cache map[string][]byte
}

// Bir xil testlar har submission'da qayta so'raladi, shuning uchun oddiy
// keshsiz S3 ga yuz minglab ortiqcha so'rov ketardi.
const cacheMaxBytes = 256 << 20

func newStore() (*store, error) {
	endpoint := os.Getenv("S3_ENDPOINT")
	if endpoint == "" {
		return nil, nil // sozlanmagan — ref'siz (inline) ishlar hamon ishlaydi
	}
	secure := strings.HasPrefix(endpoint, "https://")
	host := strings.TrimPrefix(strings.TrimPrefix(endpoint, "https://"), "http://")

	client, err := minio.New(host, &minio.Options{
		Creds:  credentials.NewStaticV4(os.Getenv("S3_KEY"), os.Getenv("S3_SECRET"), ""),
		Secure: secure,
	})
	if err != nil {
		return nil, fmt.Errorf("s3 mijozi: %w", err)
	}
	return &store{
		client:        client,
		defaultBucket: os.Getenv("S3_BUCKET"),
		cache:         make(map[string][]byte),
	}, nil
}

func (s *store) split(ref string) (bucket, key string, err error) {
	trimmed := strings.TrimPrefix(ref, "s3://")
	if trimmed == ref {
		return "", "", fmt.Errorf("s3:// bilan boshlanmagan havola: %q", ref)
	}
	bucket, key, found := strings.Cut(trimmed, "/")
	if !found || key == "" {
		return "", "", fmt.Errorf("kalitsiz havola: %q", ref)
	}
	return bucket, key, nil
}

func (s *store) get(ctx context.Context, ref string) ([]byte, error) {
	if s == nil || s.client == nil {
		return nil, fmt.Errorf("S3 sozlanmagan, %q ni o'qib bo'lmaydi", ref)
	}
	s.mu.Lock()
	if data, ok := s.cache[ref]; ok {
		s.mu.Unlock()
		return data, nil
	}
	s.mu.Unlock()

	bucket, key, err := s.split(ref)
	if err != nil {
		return nil, err
	}
	obj, err := s.client.GetObject(ctx, bucket, key, minio.GetObjectOptions{})
	if err != nil {
		return nil, fmt.Errorf("%s: %w", ref, err)
	}
	defer obj.Close()

	data, err := io.ReadAll(obj)
	if err != nil {
		return nil, fmt.Errorf("%s: %w", ref, err)
	}

	s.mu.Lock()
	// Sodda strategiya: chegaradan oshsa keshni tozalaymiz. Testlar
	// to'plami odatda kichik, LRU murakkabligi bu yerda ortiqcha.
	if s.size()+len(data) > cacheMaxBytes {
		s.cache = make(map[string][]byte)
	}
	s.cache[ref] = data
	s.mu.Unlock()
	return data, nil
}

func (s *store) size() int {
	total := 0
	for _, v := range s.cache {
		total += len(v)
	}
	return total
}
