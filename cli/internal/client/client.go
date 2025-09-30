package client

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
)

type Client struct {
	BaseURL        string
	IdempotencyKey string
	HTTP           *http.Client
}

func New(baseURL, idem string) *Client {
	if baseURL == "" {
		baseURL = "http://127.0.0.1:8000"
	}
	return &Client{
		BaseURL:        strings.TrimRight(baseURL, "/"),
		IdempotencyKey: idem,
		HTTP:           &http.Client{Timeout: 30 * time.Second},
	}
}

func (c *Client) doJSON(method, path string, reqBody any, out any) error {
	u := c.BaseURL + path
	var body io.Reader
	if reqBody != nil {
		buf, err := json.Marshal(reqBody)
		if err != nil {
			return err
		}
		body = bytes.NewReader(buf)
	}
	req, err := http.NewRequest(method, u, body)
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	if c.IdempotencyKey != "" {
		req.Header.Set("Idempotency-Key", c.IdempotencyKey)
	}

	res, err := c.HTTP.Do(req)
	if err != nil {
		return err
	}
	defer res.Body.Close()

	respBytes, err := io.ReadAll(res.Body)
	if err != nil {
		return err
	}

	if res.StatusCode >= 200 && res.StatusCode < 300 {
		if out != nil && len(respBytes) > 0 {
			if err := json.Unmarshal(respBytes, out); err != nil {
				return fmt.Errorf("decode %s %s: %w\nbody: %s", method, path, err, string(respBytes))
			}
		}
		return nil
	}

	var apErr APIError
	if err := json.Unmarshal(respBytes, &apErr); err == nil && (apErr.Err != "" || apErr.Message != "") {
		return &apErr
	}
	return fmt.Errorf("http %s %s: %d\nbody: %s", method, path, res.StatusCode, string(respBytes))
}

// Convenience wrappers

func (c *Client) CreateTenant(name string) (TenantOut, error) {
	var out TenantOut
	err := c.doJSON("POST", "/v1/tenants", map[string]any{"name": name}, &out)
	return out, err
}

func (c *Client) CreateVRF(tenantID, name string, rd *string) (VrfOut, error) {
	payload := map[string]any{"tenant_id": tenantID, "name": name}
	if rd != nil && *rd != "" {
		payload["rd"] = *rd
	}
	var out VrfOut
	err := c.doJSON("POST", "/v1/vrfs", payload, &out)
	return out, err
}

func (c *Client) CreatePrefix(vrfID, cidr, status, desc string) (PrefixOut, error) {
	payload := map[string]any{"vrf_id": vrfID, "cidr": cidr, "status": status, "description": desc}
	var out PrefixOut
	err := c.doJSON("POST", "/v1/prefixes", payload, &out)
	return out, err
}

func (c *Client) CarveChildren(prefixID string, mask, count int) ([]PrefixOut, error) {
	var out []PrefixOut
	err := c.doJSON("POST", "/v1/prefixes/"+prefixID+"/children",
		map[string]any{"mask": mask, "count": count, "strategy": "first-fit"}, &out)
	return out, err
}

func (c *Client) NextIP(prefixID string) (NextIPOut, error) {
	var out NextIPOut
	err := c.doJSON("POST", "/v1/prefixes/"+prefixID+"/ips/next", nil, &out)
	return out, err
}
